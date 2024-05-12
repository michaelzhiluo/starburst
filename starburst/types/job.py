import copy
import time
from typing import Any, Dict


class Job(object):
    """
    Represents a generic job for the Starburst job scheduler.
    """

    def __init__(self,
                 name: str,
                 image: str = 'ubuntu',
                 run: str = None,
                 resources: dict = {}):
        """
        Args:
            name (str): The name of the job.
            arrival (float): The timestamp when the job arrived in the system.
            runtime (float): The runtime (estimated in seconds) of the job.
            yaml (dict): The yaml configuration of the job.
            resources (dict): The resources required by the job.
        """
        self._name = name
        self._image = image
        self._run = run
        self._resources = resources

        # If job is preempted from cloud or not...
        self._preempt = False

        # Arrival time indicates when the inter-cluster manager receives the job.
        self._arrival = None
        self._runtime = None
        self._start = None
        self._end = None
        # Seconds until job times out from the cluster.
        self._timeout = None

        self._annotations = {}
        self._yaml = {}

    def set_annotations(self, annotations: dict):
        self._annotations = annotations

    def set_arrival(self, time: float):
        self._arrival = time

    def set_name(self, name: str):
        self._name = name

    def set_timeout(self, timeout: float):
        self._timeout = timeout

    def set_runtime(self):
        if 'estimated_runtime' in self.annotations:
            self._runtime = (float)(self.annotations['estimated_runtime'])
        else:
            self._runtime = 1

    def set_resources(self, resources: dict):
        self._resources = resources

    def set_yaml(self, yaml: dict):
        self._yaml = yaml

    def set_preempt(self, preempt: bool):
        self._preempt = preempt

    @staticmethod
    def from_yaml_config(config: Dict[str, Any]):
        copy_config = copy.deepcopy(config)

        job = Job(
            name=config.pop('name', None),
            image=config.pop('image', None),
            resources=config.pop('resources', {}),
            run=config.pop('run', ''),
        )
        job_annotations = config.pop('annotations', None)
        job.set_annotations(job_annotations)
        job.set_yaml(copy_config)
        return job

    @property
    def preempt(self):
        return self._preempt

    @property
    def annotations(self):
        return self._annotations

    @property
    def arrival(self):
        return self._arrival

    @property
    def end(self):
        return self._end

    @property
    def image(self):
        return self._image

    @property
    def name(self):
        return self._name

    @property
    def resources(self):
        return self._resources

    @property
    def run(self):
        return self._run

    @property
    def runtime(self):
        return self._runtime

    @property
    def start(self):
        return self._start

    @property
    def timeout(self):
        return self._timeout

    @property
    def yaml(self):
        return self._yaml

    def __repr__(self):
        return (f"Job, name: {self.name}, submit: {self.arrival}, "
                f"start: {self.start}, "
                f"end: {self.end}, resources: {self.resources}")
