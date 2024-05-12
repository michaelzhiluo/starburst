# Defines the waiting policies for the queue. A policy can introspect the
# queue and cluster and decide what action to take.
from asyncio import subprocess
import logging
import os
import tempfile
import threading
import time
from typing import Dict, List

from starburst.cluster_managers import Manager, LogClusterManager, SkyPilotManager
from starburst.policies import waiting_policies
from starburst.types.job import Job

logger = logging.getLogger(__name__)

POLICY_CONFIG_TEMPLATE = {
    'waiting_policy': 'infinite',
    'waiting_coeff': -1,
    'queue_policy': 'fifo',
    'min_waiting_time': 10,
    'loop': False,
}


def get_policy(policy_config: Dict[str, str]):
    """ Get the policy object based on the policy name. """
    if policy_config['waiting_policy'] is None:
        return FIFOOnpremOnlyPolicy
    else:
        return HybridCloudPolicy


class BasePolicy(object):

    def __init__(self, onprem_manager: Manager, cloud_manager: Manager):
        self.onprem_manager = onprem_manager
        self.cloud_manager = cloud_manager

    def process_queue(self, queue):
        raise NotImplementedError("Policy must implement process method.")


# Similar to YARN CapacityScheduler. Jobs wait in queue until the onprem
# cluster can fit the job.
class FIFOOnpremOnlyPolicy(BasePolicy):
    """
    Implements FIFO submission to only onprem. Jobs wait indefinitely
    in the queue until the onprem cluster can fit the job.
    """

    def process_queue(self, job_queue: List[Job]):
        """
        Process in FIFO order. Block the queue if the onprem cluster
        cannot fit the job and return.
        """
        if job_queue:
            # Check if the onprem cluster can fit the job
            if self.onprem_manager.can_fit(job_queue[0]):
                # Remove from queue
                job = job_queue.pop(0)
                # Submit the job
                self.onprem_manager.submit_job(job)


class HybridCloudPolicy(BasePolicy):
    """
    Implements FIFO submission to onprem and cloud. 
    
    If job has been waiting longer than a threshold, submit to cloud. """

    def __init__(
        self,
        onprem_manager: Manager,
        cloud_manager: Manager,
        policy_config: Dict[str, str] = POLICY_CONFIG_TEMPLATE,
    ):
        super().__init__(onprem_manager, cloud_manager)
        copy_dict = dict(POLICY_CONFIG_TEMPLATE)
        copy_dict.update(policy_config)
        self.policy_config = copy_dict
        self.waiting_policy = policy_config['waiting_policy']
        self.waiting_coeff = policy_config['waiting_coeff']
        self.queue_policy = policy_config['queue_policy']
        self.loop = policy_config['loop']
        self.min_waiting_time = policy_config['min_waiting_time']

        self.waiting_policy_cls = waiting_policies.get_waiting_policy_cls(
            self.waiting_policy)(self.waiting_coeff)

    def process_queue(self, job_queue: List[Job]):

        # Loop through queue to release jobs which timeout
        if job_queue:
            print("Queue", job_queue)
            for job in job_queue:
                wait_time = time.time() - job.arrival
                if job.timeout is None:
                    job.set_timeout(
                        self.waiting_policy_cls.compute_timeout(job))
                timeout = max(job.timeout, self.min_waiting_time)
                print(f'{job} has waited {wait_time}, max timeout {timeout}')
                job_timed_out = wait_time >= timeout
                if job_timed_out:
                    job_queue.remove(job)
                    if self.waiting_policy == waiting_policies.WaitingPolicyEnum.STAR.value and not job.preempt and job.runtime > waiting_policies.STAR_WAIT_THRESHOLD:
                        # Jobs longer than 5 min are preempted from cloud back to onprem.
                        logger.debug(f'Preempted job entered || job {job.name} | queue {job_queue}')
                        # Start thread
                        job.set_preempt(True)
                        self.cloud_manager.submit_job(job)
                        submit_preempted_job(job, job_queue)
                    else:
                        job.set_preempt(False)
                        self.cloud_manager.submit_job(job)
                    print(f"{job} timed out")
                    

            # Loop through the queue for submitting jobs to on-prem.
            for job in job_queue:
                can_fit = self.onprem_manager.can_fit(job)
                if can_fit:
                    print(f"{job} can fit")
                    job_queue.remove(job)
                    self.onprem_manager.submit_job(job)
                else:
                    if self.loop:
                        continue
                    break

def resubmit_job(job: Job, job_queue: List[Job]):
    # Emulates running for 300 - 2 seconds
    time.sleep(waiting_policies.STAR_WAIT_THRESHOLD)
    # Submit job to on-prem
    job.set_timeout(None)
    job_queue.append(job)
    print(f"Job queue: {job_queue} <------------- ")
    print(f"Resubmitted {job} to on-prem")

def submit_preempted_job(job, job_queue: List[Job]):
    # Resubmit preempted job in a separate thread that sleeps for 29.8 seconds
    t = threading.Thread(target=resubmit_job, args=(job,job_queue))
    t.start()