import argparse
import grpc
import logging

from starburst.event_sources.grpc.protogen import job_submit_pb2_grpc, job_submit_pb2

DEFAULT_IP = 'localhost'
DEFAULT_PORT = 10000

def parseargs():
    parser = argparse.ArgumentParser(description='GRPC dummy client that generates and sends job submission messages.')
    parser.add_argument('--port', '-p', type=int, default=DEFAULT_PORT, help='GRPC Port')
    parser.add_argument('--ip', '-i', type=str, default=DEFAULT_IP, help='GRPC IP addresss')
    args = parser.parse_args()
    return args

def run_client(ip, port):
    with grpc.insecure_channel(f'{ip}:{port}') as channel:
        stub = job_submit_pb2_grpc.JobSubmissionStub(channel)
        print("-------------- SubmitJob --------------")
        ret = stub.SubmitJob(job_submit_pb2.JobMessage(JobYAML="Hi!"))
        print(f"Got retcode {ret.retcode}")


if __name__ == '__main__':
    logging.basicConfig()
    args = parseargs()
    logging.info(args)
    run_client(args.ip, args.port)