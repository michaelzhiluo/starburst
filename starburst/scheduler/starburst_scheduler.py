"""
Starburst scheduler.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import time
import traceback
from typing import Any, Dict

from starburst.policies import queue_policies
from starburst.cluster_managers import Manager, KubernetesManager, LogClusterManager, SkyPilotManager
from starburst.types.events import BaseEvent, EventTypes, SchedTick, \
    JobAddEvent

logger = logging.getLogger(__name__)

SCHED_TICK = 0.1

def setup_cluster_manager(cluster_config: Dict[str, Any]) -> Manager:
    """ Create a cluster manager based on the cluster config. """
    cluster_type = cluster_config['cluster_type']
    cluster_manager_cls = None
    if cluster_type == 'k8':
        cluster_manager_cls = KubernetesManager
    elif cluster_type == 'log':
        cluster_manager_cls = LogClusterManager
    elif cluster_type == 'skypilot':
        cluster_manager_cls = SkyPilotManager
    else:
        raise ValueError("Invalid cluster type: {}".format(cluster_type))

    # Get the constructor of the class
    constructor = cluster_manager_cls.__init__
    # Get the parameter names of the constructor
    class_params = constructor.__code__.co_varnames[1:constructor.__code__.
                                                    co_argcount]

    # Filter the dictionary keys based on parameter names
    args = {k: v for k, v in cluster_config.items() if k in class_params}

    # Create an instance of the class with the extracted arguments
    return cluster_manager_cls(**args)


class StarburstSchedulerv0:
    """ Starburst scheduler v0.
    
    Description: Starburst scheduler is responsible for scheduling jobs on both
    the on-prem and cloud clusters. It is also responsible for handling events,
    such as job add events (JobAdd) and scheduling ticks (SchedulerTick).
    """

    def __init__(
        self,
        event_queue: asyncio.Queue,
        event_logger: object,
        clusters: Dict[str, Any],
        policy_config: Dict[str, str],
    ):
        """
        Main Starburst scheduler class.

        Responsible for processing events in the provided event queue.

        Args:
            event_queue (asyncio.Queue): Event queue for asynchronous
                                         event processing.
            event_logger (object): Event logger used for debug and
                                   storing events in the system.
            onprem_cluster_name (str): Name of the on-prem cluster (the name
                                       of the context in kubeconfig).
            cloud_config (Dict[str, object]): Configuration for the cloud.
        """
        # Scheduler objects
        self.event_queue = event_queue
        self.event_logger = event_logger

        # Job queue
        # TODO(mluo): Move to within Kubernetes instead.
        self.job_queue = []

        self.cluster_managers = {}
        # Create the cluster maangers for on-prem and cloud.
        for cluster_cls, cluster_config in clusters.items():
            self.cluster_managers[cluster_cls] = setup_cluster_manager(
                cluster_config)

        self.policy_config = policy_config
        # Set up policy
        queue_policy_class = queue_policies.get_policy(self.policy_config)
        self.queue_policy = queue_policy_class(
            self.cluster_managers['onprem'],
            self.cluster_managers['cloud'],
            policy_config=self.policy_config)
        self.executor = ThreadPoolExecutor(max_workers=1)

    def process_event(self, event: BaseEvent):
        '''
        Sends an event to the appropriate processor.

        Args:
            event (BaseEvent): Event to process. Can be SchedulerTick
                               or JobAddEvent.
        '''
        # TODO: Timeout event for job
        if event.event_type == EventTypes.SCHED_TICK:
            assert isinstance(event, SchedTick), "Event is not a SchedTick"
            self.processor_sched_tick_event(event)
        elif event.event_type == EventTypes.JOB_ADD:
            assert isinstance(event, JobAddEvent), "Event is not a JobAddEvent"
            self.processor_job_add_event(event)
        else:
            raise NotImplementedError(
                f"Event type {event.event_type} is not supported.")

    def processor_sched_tick_event(self, event: SchedTick):
        """
        Scheduler tick event. This is the periodic event for the scheduler.

        This is where the scheduler will process the queue and make
        intelligent decisions.
        """
        if self.event_logger:
            self.event_logger.log_event(event)
        # Process the queue
        # self.queue_policy.process_queue(self.job_queue)

    def processor_job_add_event(self, event: JobAddEvent):
        """
        Process an add job event. This is where the job is added to the
        scheduler queue.

        Args:
            event (JobAddEvent): Job add event.
        """
        if self.event_logger:
            self.event_logger.log_event(event)
        add_job = event.job
        add_job.set_arrival(time.time())
        add_job.set_runtime()
        print(add_job.runtime)
        self.job_queue.append(add_job)
    
    async def process_queue_async(self):
        """
        Wrapper to run process_queue in a separate thread and await its completion.
        """
        loop = asyncio.get_running_loop()
        # Run the potentially blocking process_queue call in a separate thread
        await loop.run_in_executor(self.executor, self.queue_policy.process_queue, self.job_queue)


    async def scheduler_loop(self):
        """
        Main scheduler loop.

        This is the main loop for the scheduler. It will process events
        """
        while True:
            loop_start_time = time.perf_counter()
            event = None
            try:
                if not self.event_queue.empty():
                    event = self.event_queue.get_nowait()
            except Exception as e:
                logger.debug(f"Exception: {e}: {traceback.print_exc()}")

            if event:
                self.process_event(event)

            await self.process_queue_async()

            loop_end_time = time.perf_counter()
            delta = loop_end_time - loop_start_time
            if delta < SCHED_TICK:
                await asyncio.sleep(SCHED_TICK - delta)