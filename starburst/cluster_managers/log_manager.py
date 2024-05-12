import math
import threading
import time as time
from typing import List
from starburst.policies.waiting_policies import STAR_WAIT_THRESHOLD
from starburst.types.job import Job
from starburst.utils import LogManager


class LogClusterManager(object):
    """
    A cluster manager acting over a log file, used for testing inter-cluster features.

    This cluster manager assumes the log file is a cluster of infinite resources.
    """

    def __init__(self, cluster_name: str, log_file: str):
        self.cluster_name = cluster_name
        self.log_file = log_file
        self.logger = LogManager(cluster_name, self.log_file)

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
        estimated_runtime = job.annotations.get('estimated_runtime', None)
        log_string = (f'Job: {job.name} | '
                      f'Arrival: {job.arrival} | '
                      f'Start:  {time.time()} | '
                      f'Runtime: {estimated_runtime} | ')
        for r_type, r_count in job.resources.items():
            log_string += f'{r_type}: {r_count} | '
        log_string += f'Preempted: {job.preempt}'
        self.logger.append(log_string)