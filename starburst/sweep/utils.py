import logging
import math
import os
from typing import Any, Dict, Tuple

from kubernetes import client, config
import yaml

from starburst.policies.waiting_policies import WaitingPolicyEnum
from starburst.sweep import training_dataset

logger = logging.getLogger(__name__)


class RunConfig:

    def __init__(self, config_dict):
        self.__dict__.update(config_dict)


def load_yaml_file(file_path: str) -> dict:
    """
    Loads a YAML file from a specified file path.

    Args:
        file_path (str): Path to YAML file.
    """
    file_path = os.path.abspath(file_path)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Sweep config YAML not found: {file_path}")
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data


def save_yaml_object(obj_dict: dict, path: str) -> None:
    """
    Saves a dictionary of objects to a YAML file.

    Args:
        obj_dict (dict): Dictionary of objects to save.
        path (str): Path to save YAML file.
    """
    path = os.path.abspath(path)
    yaml_runs = yaml.dump(obj_dict)
    with open(path, "w") as f:
        f.write(yaml_runs)


def sample_gpu_train_job(gpu: int, duration: float) -> Tuple[int, str]:
    """
    Returns a closest real-life training job closest to (gpu, duration) pair.
    """
    jobs = [(j[1], j[3]) for j in training_dataset.ESTIMATED_TIMES
            if j[2] == gpu]
    min_delta = math.inf
    min_id = 0
    for i in range(len(jobs)):
        delta = abs(jobs[i][0] - duration)
        if delta <= min_delta:
            min_delta = delta
            min_id = i
    return jobs[min_id]


def check_empty_cluster(clusters: Dict[str, Any]) -> bool:
    """
    Returns true if there are no pods/jobs in both on-prem and cloud clusters.
    """
    for _, cluster_config in clusters.items():
        if cluster_config['cluster_type'] != 'k8':
            continue
        cluster_args = cluster_config
        kube_cluster_name = cluster_args['cluster_name']
        config.load_kube_config(context=kube_cluster_name)
        api = client.CoreV1Api()
        pods = api.list_namespaced_pod(namespace='default')
        for pod in pods.items:
            if "chakra" in pod.metadata.name:
                continue
            return False
    return True


def clear_clusters(clusters: Dict[str, Any]):
    """
    Automates clearing of cluster state by removing event, logs, and pods
    on both onprem and cloud cluster.
    """
    while True:
        try:
            api_batch_list = []
            for _, cluster_config in clusters.items():
                if cluster_config['cluster_type'] != 'k8':
                    continue
                cluster_args = cluster_config
                kube_cluster_name = cluster_args['cluster_name']
                # Fetching cluster APIs
                config.load_kube_config(context=kube_cluster_name)
                api = client.CoreV1Api()
                api_batch = client.BatchV1Api()
                api_batch_list.append(api_batch)
                # Deleting all jobs.
                jobs_list = api_batch.list_namespaced_job(namespace='default')
                for job in jobs_list.items:
                    logger.debug(f'Attempting to Delete {job.metadata.name}')
                    api_batch.delete_namespaced_job(
                        name=job.metadata.name,
                        namespace='default',
                        body=client.V1DeleteOptions(
                            propagation_policy='Foreground',
                            grace_period_seconds=0))
                # Deleting all pod events.
                api.delete_collection_namespaced_event(
                    namespace='default',
                    body=client.V1DeleteOptions(
                        propagation_policy='Foreground',
                        grace_period_seconds=0),
                )
                # Deleting all pods.
                pods = api.list_namespaced_pod(namespace='default')
                for pod in pods.items:
                    if "chakra" in pod.metadata.name:
                        continue
                    api.delete_namespaced_pod(name=pod.metadata.name,
                                              namespace=pod.metadata.namespace,
                                              body=client.V1DeleteOptions())
        except Exception as e:
            logger.debug(
                f'Exception {e} occurred while clearing cluster state. '
                'Retrying...')
        else:
            done = True
            for api_batch in api_batch_list:
                jobs_list = api_batch.list_namespaced_job(namespace='default')
                if len(jobs_list.items) != 0:
                    done = False
            if done:
                break


def create_log_directory(log_path: SyntaxWarning) -> str:
    """
    Creates a log directory for the entire sweep.

    Args:
        name (str): Name of the log directory for the current sweep.
    """
    base_log_path = os.path.abspath(log_path)
    os.makedirs(base_log_path, exist_ok=True)
    # Generate sub log directories.
    sub_logs = ["jobs/", "debug/", "events/"]
    for s_log in sub_logs:
        temp_path = f"{base_log_path}/{s_log}"
        os.makedirs(temp_path, exist_ok=True)


def estimate_waiting_coeff(waiting_policy: str, waiting_budget: float,
                           jobs: Dict[Any, Any]):
    """
    Estimate the waiting coefficient based on the waiting policy, waiting
    budget and generated job data.
    """
    total_jobs = len(jobs)
    assert total_jobs > 0, "No jobs to schedule."
    workload_type = jobs[0]['workload_type']

    avg_job_duration = 0
    avg_job_size = 0
    for _, job in jobs.items():
        avg_job_duration += job['job_duration']
        resources = job['resources']
        if workload_type == 'cpu_sleep':
            avg_job_size += resources['cpu']
        elif 'gpu' in workload_type:
            avg_job_size += resources['gpu']
        elif 'artifact' in workload_type:
            # CPU as a proxy for GPUs
            avg_job_size += resources['cpu']
    avg_job_duration /= float(total_jobs)
    avg_job_size /= float(total_jobs)

    if waiting_policy == WaitingPolicyEnum.INFINITE.value or waiting_policy == WaitingPolicyEnum.ZERO.value:
        return -1
    elif waiting_policy == WaitingPolicyEnum.CONSTANT.value:
        return waiting_budget * avg_job_duration
    elif waiting_policy == WaitingPolicyEnum.RUNTIME.value:
        return waiting_budget
    elif waiting_policy == WaitingPolicyEnum.RESOURCE.value or waiting_policy == WaitingPolicyEnum.STAR.value:
        return waiting_budget * avg_job_duration / avg_job_size
    elif waiting_policy == WaitingPolicyEnum.COMPUTE.value:
        return waiting_budget / avg_job_size
    else:
        raise ValueError(f"Invalid waiting policy: {waiting_policy}.")