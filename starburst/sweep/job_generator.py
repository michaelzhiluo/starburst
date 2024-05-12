import numpy as np
from typing import Dict

from jinja2 import Environment, select_autoescape, FileSystemLoader
import yaml

from starburst.sweep import utils

JOB_GEN_ARRAY = [
    "arrival_dist",
    "arrival_param",
    "min_arrival_time",
    "mean_duration",
    "min_duration",
    "max_duration",
    "image",
    "cpu_dist",
    "cpu_sizes",
    "gpu_dist",
    "gpu_sizes",
]
JOB_TEMPLATE_PATH = 'generated_job.jinja'


class JobGenerator(object):
    """
    Base class for generating jobs.

    The job generator is responsible for generating job resources,
    interarrival times, and durations.
    """

    def __init__(self, config) -> None:
        self.config = config

    def get_resources(self) -> Dict[str, int]:
        """
        Returns a dictionary of CPU and GPU resource request for the job.
        """
        return {"cpu": 1, "gpu": 0}

    def get_interarrival(self) -> float:
        """
        Returns the interarrival time of the job in seconds.
        """
        arrival_dist = self.config["arrival_dist"]
        arrival_param = self.config["arrival_param"]
        job_submit_time = 0
        if arrival_dist == "uniform":
            job_submit_time = arrival_param
        elif arrival_dist == "poisson":
            job_submit_time = np.random.exponential(scale=1 / (arrival_param/3600.0))
        else:
            raise ValueError(f"Unknown arrival distribution {arrival_dist},"
                             "must be uniform or poisson.")
        return max(self.config["min_arrival_time"], job_submit_time)

    def get_duration(self) -> float:
        """
        Returns the duration of the job in seconds.
        """
        mean_duration = self.config["mean_duration"]
        min_duration = self.config["min_duration"]
        max_duration = self.config["max_duration"]
        job_duration = np.random.exponential(scale=mean_duration)
        job_duration = float(np.clip(job_duration, min_duration, max_duration))
        return job_duration

    def get_jinja_dict(self, job: dict) -> dict:
        """
        Returns a dictionary of values to use for the jinja template.

        Args:
                job: A dictionary containing the job_id, job_duration,
                     and resources.
        """
        return NotImplementedError

    @property
    def image(self) -> str:
        """
        Returns the image to use for this job.
        """
        return self.config["image"]

    @property
    def run_command(self) -> str:
        """
        Returns the running command to use for this job.

        Run command can also be a string template that can be formatted later.
        """
        return NotImplementedError


class CPUSleepJobGenerator(JobGenerator):
    """
    A job generator that generates CPU only sleep jobs.
    """

    def get_resources(self) -> Dict[str, int]:
        cpu_dist = self.config["cpu_dist"]
        cpus = int(np.random.choice(self.config["cpu_sizes"], p=cpu_dist))
        return {"cpu": cpus, "gpu": 0}

    def get_jinja_dict(self, job: dict):
        resources = job["resources"]
        return {
            "job_id": str(job["job_id"]),
            "run": self.run_command.format(time=job["job_duration"]),
            "cpu": resources["cpu"],
            "gpu": resources["gpu"],
            "image": self.image,
            "estimated_runtime": job["job_duration"],
        }

    @property
    def run_command(self):
        return "echo '||' && sleep {time}"


class GPUSleepJobGenerator(JobGenerator):
    """
    A job generator that generates GPU only sleep jobs.
    """

    def get_resources(self) -> Dict[str, int]:
        cpu_dist = self.config["cpu_dist"]
        gpu_dist = self.config["gpu_dist"]
        cpus = int(np.random.choice(self.config["cpu_sizes"], p=cpu_dist))
        gpus = int(np.random.choice(self.config["gpu_sizes"], p=gpu_dist))
        return {"cpu": cpus, "gpu": gpus}

    def get_jinja_dict(self, job: dict):
        resources = job["resources"]
        return {
            "job_id": str(job["job_id"]),
            "run": self.run_command.format(time=job["job_duration"]),
            "cpu": resources["cpu"],
            "gpu": resources["gpu"],
            "image": self.image,
            "estimated_runtime": job["job_duration"],
        }

    @property
    def run_command(self):
        # Must add nvidia-smi to query for GPU indexes (later
        # used to plot job runs on a Gantt chart).
        return ("nvidia-smi --query-gpu=uuid --format=csv,noheader && "
                "echo '||' && sleep {time}")


# Stateful job generator, keeps track of previous gpu and training scripts.
class GPUTrainJobGenerator(JobGenerator):
    """
    A job generator that generates GPU training jobs. See training_dataset.py
    for more details.
    """

    def __init__(self, config) -> None:
        super().__init__(config)
        self.cached_values = {"gpus": 0, "run": None}

    def get_resources(self) -> Dict[str, int]:
        gpu_dist = self.config["gpu_dist"]
        gpus = int(np.random.choice(self.config["gpu_sizes"], p=gpu_dist))
        self.cached_values["gpu"] = gpus
        return {"cpu": 11 * gpus, "gpu": gpus}

    def get_duration(self):
        generated_duration = super().get_duration()
        estimated_duration, run_command = utils.sample_gpu_train_job(
            self.cached_values["gpu"], generated_duration)
        self.cached_values["run"] = f'python {run_command}'
        return estimated_duration

    def get_jinja_dict(self, job: dict):
        resources = job["resources"]
        return {
            "job_id": str(job["job_id"]),
            "run": self.run_command.format(run=self.cached_values["run"]),
            "cpu": resources["cpu"],
            "gpu": {
                "gpu": resources["gpu"]
            },
            "image": self.image,
            "estimated_runtime": job["job_duration"],
        }

    @property
    def run_command(self):
        return ("nvidia-smi --query-gpu=uuid --format=csv,noheader && "
                "echo '||' && {run}")

    @property
    def image(self):
        # All jobs work on this specific pytorch image. Do not modify.
        return "gcr.io/deeplearning-platform-release/pytorch-gpu.1-12"


# Stateful job generator, keeps track of previous gpu and training scripts.
class ArtifactEvalGenerator(JobGenerator):
    """
    A job generator that generates train jobs disguised as sleeping jobs. See training_dataset.py
    for more details.
    """

    def __init__(self, config) -> None:
        super().__init__(config)
        self.cached_values = {"cpus": 0, "run": None}

    def get_resources(self) -> Dict[str, int]:
        gpu_dist = self.config["gpu_dist"]
        gpus = int(np.random.choice(self.config["gpu_sizes"], p=gpu_dist))
        self.cached_values["gpu"] = gpus
        return {"cpu": 3 * gpus}

    def get_duration(self):
        generated_duration = super().get_duration()
        estimated_duration, run_command = utils.sample_gpu_train_job(
            self.cached_values["gpu"], generated_duration)
        self.cached_values["run"] = f'sleep {estimated_duration}'
        return estimated_duration

    def get_jinja_dict(self, job: dict):
        resources = job["resources"]
        return {
            "job_id": str(job["job_id"]),
            "run": self.run_command.format(run=self.cached_values["run"]),
            "cpu": resources["cpu"],
            "gpu": 0,
            "image": self.image,
            "estimated_runtime": job["job_duration"],
        }

    @property
    def run_command(self):
        return ("echo '||' && {run}")

    @property
    def image(self):
        # All jobs work on this specific pytorch image. Do not modify.
        return "gcr.io/sky-burst/skyburst:latest"


JOB_GENERATORS = {
    "cpu_sleep": CPUSleepJobGenerator,
    "gpu_sleep": GPUSleepJobGenerator,
    "gpu_train": GPUTrainJobGenerator,
    "artifact_eval": ArtifactEvalGenerator,
}


def generate_jobs(sweep_name: str, run_config: utils.RunConfig):
    """
    Generate jobs based on the job generation configuration.

    Args:
            run_config: The run configuration object, which specifies the
            hyperparameters for this run.
    """
    rc = run_config
    np.random.seed(rc.random_seed)

    # Get the job generator class.
    job_gen_class = None
    if rc.workload_type in JOB_GENERATORS:
        job_gen_class = JOB_GENERATORS[rc.workload_type]
    else:
        raise ValueError(f"Invalid workload type {rc.workload_type}.")

    # Initialize the job generator.
    all_params = vars(run_config)
    job_gen = job_gen_class(
        {key: all_params[key]
         for key in JOB_GEN_ARRAY if key in all_params})

    # Load the Jinja template for the corresponding workload type.
    jinja_env = Environment(loader=FileSystemLoader('./'),
                            autoescape=select_autoescape())
    template = jinja_env.get_template(JOB_TEMPLATE_PATH)

    jobs = {}
    job_index = 0
    total_submit_time = 0
    # Loop to generate jobs.
    while True:
        if total_submit_time >= rc.submit_time:
            break
        job = {
            "job_id": f'job-{job_index}-{sweep_name}',
            "workload_type": rc.workload_type,
            "image": job_gen.image,
        }
        job["resources"] = job_gen.get_resources()
        total_submit_time += job_gen.get_interarrival()
        job["submit_time"] = total_submit_time
        job["job_duration"] = job_gen.get_duration()
        jinja_dict = job_gen.get_jinja_dict(job)
        jinja_dict['job_id'] = f'job-{jinja_dict["job_id"]}-{sweep_name}'
        jinja_str = template.render(job_gen.get_jinja_dict(job))
        job_yaml = yaml.safe_load(jinja_str)
        job["job_yaml"] = job_yaml
        print(f"Job {job_index} - Arrival: {total_submit_time}; Yaml: {job_yaml}")
        jobs[job_index] = job
        job_index += 1
    return jobs
