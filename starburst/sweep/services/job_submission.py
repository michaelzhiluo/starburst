"""
Submits jobs to the on-prem cluster and cloud cluster.

Description:
This module contains the job submission service, which is responsible for
submitting jobs to the on-prem cluster and cloud cluster via the
`submission_loop` method. Jobs are submitted to cluster based on their arrival
times. When all jobs have completed, the service exits.
"""
import logging
import os
import re
import subprocess
import time
import tempfile
import traceback
from typing import Any, Dict

from kubernetes import client, config
import sky
import yaml

from starburst.sweep import utils, submit_sweep
from starburst.utils import LogManager

JOB_SUBMISSION_TICK = 0.05
JOB_COMPLETION_TICK = 1

logger = logging.getLogger(__name__)


class JobStateTracker(object):
    """
    Tracks the job submission and completion over the cloud & on-prem cluster.
    """

    def __init__(self, num_jobs):
        self.submit_state = {idx: False for idx in range(num_jobs)}
        self.finish_state = {idx: False for idx in range(num_jobs)}
        self.temp = False

    def update_submit_idx(self, idx: int, state: Any):
        """
        Updates the submission state of the job with the given index.
        """
        self.submit_state[idx] = state

    def check_if_jobs_submitted(self) -> bool:
        """
        Check if all jobs have been submitted.
        """
        return all(self.submit_state.values())

    def update_finished_jobs(self, clusters: Dict[str, Any]):
        """
        Updates the finished state of the jobs.        
        For the on-premise cluster,it polls Kubernetes for the job status.
        For the cloud-cluster, depending on the spillover configuration,
        it either polls the cloud cluster or parses the log file.

        Args:
            onprem_cluster (Dict[str, Any]): On-prem cluster configuration.
            cloud_cluster (Dict[str, Any]): Cloud cluster configuration.
        """
        for cluster_config in clusters.values():
            cluster_args = cluster_config
            cluster_name = cluster_args['cluster_name']
            cluster_type = cluster_config['cluster_type']
            if cluster_type == 'log':
                cloud_log_path = cluster_args['log_file']
                cloud_jobs = parse_spillover_jobs(file_path=cloud_log_path)
                for job_idx in cloud_jobs:
                    self.finish_state[job_idx] = True
                continue
            elif cluster_type == 'skypilot':
                if not self.temp:
                    self.temp = True
                    time.sleep(10)
                status_config = sky.status(refresh=True)
                for job_idx, job_state in self.finish_state.items():
                    if not job_state:
                        job_name = "job-" + str(job_idx)
                        if not any(job_name in job_config["name"]
                                   for job_config in status_config):
                            self.finish_state[job_idx] = True
                continue
            elif cluster_type == 'k8':
                config.load_kube_config(context=cluster_name)
                api = client.BatchV1Api()
                job_list, _, _ = api.list_namespaced_job_with_http_info(
                    namespace="default", limit=None, _continue="")
                for job_idx, job_state in self.finish_state.items():
                    try:
                        if not job_state:
                            curr_job = find_job_with_substring(
                                job_list.items, "job-" + str(job_idx))
                            if curr_job.status.succeeded == 1:
                                self.finish_state[job_idx] = True
                    except Exception:
                        pass
            else:
                raise ValueError(f"Invalid cluster type: {cluster_type}")

    def check_if_jobs_finished(self) -> bool:
        return all(self.finish_state.values())


def find_job_with_substring(jobs_http: dict, substring: str):
    for job in jobs_http:
        if substring in job.metadata.name:
            return job
    return None


def parse_spillover_jobs(file_path: str):
    """
    Parses the log file to find jobs that were spilled over to the cloud.

    Args:
            file_path (str): Path to the log file.
    """
    with open(file_path, "r") as f:
        cloud_log_list = f.read().split("\n")
    log_jobs = []
    for log in cloud_log_list:
        # Regex to find the job id and the expected job duration.
        match = re.search(r"Job: job-(\S+)-(\S+) \| Arrival: (\S+) \| Start: (\S+) \| Runtime: (\S+) \| cpu: (\S+) \| gpu: (\S+) \| Preempted: (\S+)", log)

        if match is None:
            continue
        match = match.groups()
        if match:
            # Convert the job id to an int.
            job_id = int(match[0])
            preempted = match[7]
            if preempted.lower() == "true":
                continue
            log_jobs.append(job_id)
    return log_jobs


def get_job_submission_log_path(name: str):
    """
    Retrives the path to the job submission log file.
    """
    path = (f"{submit_sweep.LOG_DIRECTORY.format(name=name)}"
            "/debug/job_submission_thread.log")
    return os.path.abspath(path)


def get_event_submission_log_path(name: str, idx: int):
    """
    Retrives the path to the event submission log file.
    """
    path = (f"{submit_sweep.LOG_DIRECTORY.format(name=name)}"
            f"/events/{idx}.log")
    return os.path.abspath(path)


def submit_job_to_scheduler(job_yaml: dict):
    with tempfile.NamedTemporaryFile(mode="w") as f:
        temp_file_path = f.name
        yaml.safe_dump(job_yaml, f)
        logger.debug(
            f"****** Job Sent to submit_job.py at Time {time.time()} ******")
        subprocess.run([
            "python3",
            "-m",
            "starburst.drivers.submit_job",
            "--job-yaml",
            temp_file_path,
        ])


def submission_loop(
    jobs: Dict[Any, Any],
    clusters: Dict[str, Any],
    sweep_name: str,
    run_index: int,
    file_logger: LogManager,
):
    """
    Logic for submitting jobs to the scheduler. Only returns when all jobs
    have been submitted and completed running on the cluster.
    """
    total_jobs = len(jobs)
    job_tracker = JobStateTracker(total_jobs)

    # Primary loop for submitting jobs to the scheduler.
    # Will submit jobs until all jobs have been submitted.
    file_logger.append(f"Submitting {total_jobs} jobs...")
    submission_offset = time.time()
    job_index = 0
    while True:
        # Offset a job's submit time by the Unix epoch time.
        if time.time() > jobs[job_index]["submit_time"] + submission_offset:
            job = jobs[job_index]
            submit_job_to_scheduler(job["job_yaml"])
            submit_time = time.time()
            job_file_path = "../sweep_logs/" + str(sweep_name) + "/jobs/" + str(run_index) + ".yaml"
            job_data = {}
            with open(job_file_path, "r") as f:
                job_data = yaml.safe_load(f)
                job_data[job_index]['scheduler_submit_time'] = submit_time
            with open(job_file_path, "w") as f:
                yaml.dump(job_data, f)
            
            job_tracker.update_submit_idx(job_index, submit_time)
            file_logger.append(f"Submitting Job {job_index}: {str(job)} "
                               f"during time {submit_time}.")
            job_index += 1
        if job_index >= total_jobs:
            break
        time.sleep(JOB_SUBMISSION_TICK)
    assert (job_tracker.check_if_jobs_submitted()
            ), "Not all jobs were submitted to the scheduler."

    # Once all jobs have been submitted, continually check the status of the
    # jobs until all jobs have completed.
    print("Job submission complete; waiting for all jobs to complete...")
    file_logger.append(f"Waiting for {total_jobs} jobs to complete...")
    while True:
        if job_tracker.check_if_jobs_finished():
            break
        job_tracker.update_finished_jobs(clusters)
        file_logger.append("Finished Jobs State: " +
                           str(job_tracker.finish_state))
        time.sleep(JOB_COMPLETION_TICK)


def job_submission_service(jobs: Dict[Any, Any], clusters: Dict[str, Any],
                           sweep_name: str, run_index: int):
    """
    Calls loop that submit jobs to the scheduler. 
    If an error occurs during the submission loop, the error is logged.
    """
    submission_file_logger = LogManager(
        "job_submission_service", get_job_submission_log_path(sweep_name))
    try:
        submission_loop(
            jobs=jobs,
            clusters=clusters,
            sweep_name=sweep_name,
            run_index=run_index,
            file_logger=submission_file_logger,
        )
    except Exception:
        # If an error occrus during job submission loop, log the error
        # and move onto the next run in the sweep.
        submission_file_logger.append(traceback.format_exc() + "\n")
        pass
    submission_file_logger.close()