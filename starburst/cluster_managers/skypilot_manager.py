import math
import multiprocessing as mp
import time as time
from typing import List
import uuid

import sky

from starburst.types.job import Job


def launch_skypilot_job(job_name, job_command, job_resources, preempted=False):
    task = sky.Task(
        job_name,
        workdir=None,
        setup=None,
        run=job_command,
    )
    num_cpus = job_resources['cpu']
    num_cpus = f'{num_cpus}+'
    num_gpus = None if job_resources['gpu'] == 0 else {
        'V100': job_resources['gpu']
    }
    task.set_resources(
        {sky.Resources(cloud=sky.GCP(), cpus=num_cpus, accelerators=num_gpus)})
    job_id = str(uuid.uuid4())[:8]
    sky.launch(
        cluster_name=f'{job_name}-{job_id}',
        task=task,
        idle_minutes_to_autostop=1,
        down=True,
        detach_setup=True,
        detach_run=True,
        stream_logs=False,
    )


class SkyPilotManager(object):
    """
    A cluster manager acting over SkyPilot.

    Assumes Skypilot manages a cluster of infinite resources.
    """

    def __init__(self, cluster_name: str):
        self.cluster_name = cluster_name

    def get_cluster_resources(self):
        """ Gets total cluster resources for each node."""
        cluster_resources = {}
        cluster_resources[self.cluster_name] = {
            'cpu': math.inf,
            'memory': math.inf,
            'gpu': math.inf
        }
        return cluster_resources

    def get_allocatable_resources(self):
        return self.get_cluster_resources()

    def can_fit(self, job: Job):
        return True

    def submit_job(self, job: Job):
        print(
            f'***************Submitting Skypilot Job: {job.name}***************'
        )
        job_process = mp.Process(
            target=launch_skypilot_job,
            args=(
                job.name,
                job.run,
                job.resources,
            ),
        )
        job_process.start()