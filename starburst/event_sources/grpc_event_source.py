# THIS IS WIP - use this as a template for your own GRPC event source.
# Need to compile grpc protobufs to make this work.

import logging
from asyncio import Queue

import grpc

from concurrent import futures

from starburst.event_sources.base_event_source import BaseEventSource
from types.events import JobAddEvent

logger = logging.getLogger(__name__)


class JobSubmissionServicer(...):
    # Implements the GRPC Servicer for Job submissions from clients
    def __init__(self, event_queue: Queue, debug_mode: bool = False):
        self.event_queues = event_queue
        self.debug_mode = debug_mode
        super(JobSubmissionServicer, self).__init__()

    def SubmitJob(self, request: ..., context):
        event = JobAddEvent(job=request.job)
        self.event_queues.put_nowait(event)
        if self.debug_mode:
            logger.debug(f"Got event: {str(event)}")
        return ...


class JobSubmissionSource(BaseEventSource):
    """Runs a grpc server to get job submissions"""

    def __init__(self, output_queue: Queue, server_port: int):
        super(JobSubmissionSource, self).__init__(output_queue)
        futures_pool = futures.ThreadPoolExecutor(max_workers=10)
        self.server = grpc.aio.server(futures_pool)
        job_submission_pb2_grpc.add_JobSubmissionServicer_to_server(
            JobSubmissionServicer(self.output_queue), self.server
        )
        self.server.add_insecure_port(f"[::]:{server_port}")

    async def event_generator(self):
        """
        Long running loop that generates events indefinitely
        :return:
        """
        await self.server.start()
        await self.server.wait_for_termination()

    def __del__(self):
        self.server.stop(grace=0)
