from typing import List
from starburst.types.job import Job


class Manager(object):
    """
    General manager object.

    Serves as the base class for the compatibility layer across cluster
    managers.
    """

    def __init__(self, cluster_name: str):
        self.cluster_name = cluster_name

    def get_cluster_resources(self):
        raise NotImplementedError

    def get_allocatable_resources(self):
        raise NotImplementedError

    def can_fit(self, job: Job) -> bool:
        raise NotImplementedError

    def submit_job(self, job: Job):
        raise NotImplementedError

    def get_job_status(self, job_name):
        raise NotImplementedError

    @staticmethod
    def convert_yaml(job: Job):
        raise NotImplementedError
