import logging
from asyncio import Queue
from concurrent import futures

import grpc

from starburst.event_sources.grpc.protogen import job_submit_pb2_grpc
from starburst.event_sources.grpc.job_submit_event_source import JobSubmissionServicer

logging.basicConfig(level=logging.DEBUG)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    q = Queue()
    job_submit_pb2_grpc.add_JobSubmissionServicer_to_server(
        JobSubmissionServicer(q, debug_mode=True), server)
    server.add_insecure_port('[::]:30000')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
