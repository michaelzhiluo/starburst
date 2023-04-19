import json
from multiprocessing import Pool
import os

from skyburst.traces import philly_utils


class JobTrace:
    """Encapsulates a job."""
    def __init__(self, status, jobid, attempts, submitted_time, user):
        """Records job parameters and computes key metrics.

           Stores the passed in arguments as well as the number of GPUs
           requested by the job. In addition, computes the queueing delay
           as defined as the delta between the submission time and the start
           time of the first attempt. Finally, computes run time as defined
           as the delta between the initial attempt's start time and the last
           attempt's finish time.

           NOTE: Some jobs do not have any recorded attempts, and some attempts
           have missing start and/or end times. A job's latest attempt having no
           end time indicates that the job was still running when the log data
           was collected.

           Args:
               status: One of 'Pass', 'Killed', 'Failed'.
               jobid: The hash of the job id.
               attempts: A list of dicts, where each dict contains the following keys:
                   'start_time': The start time of the attempt.
                   'end_time': The end time of the attempt.
                   'detail': A list of nested dicts where each dict contains 
                             the following keys:
                        'ip': The server id.
                        'gpus': A list of the GPU ids allotted for this attempt.
                submitted_time: The time the job was submitted to the queue.
                user: The user's id.            
        """
        self._status = status
        self._jobid = jobid
        for attempt in attempts:
            attempt['start_time'] = philly_utils.parse_date(
                attempt['start_time'])
            attempt['end_time'] = philly_utils.parse_date(attempt['end_time'])
        self._attempts = attempts
        self._submitted_time = philly_utils.parse_date(submitted_time)
        self._user = user

        if len(self._attempts) == 0:
            self._num_gpus = None
            self._run_time = None
            self._queueing_delay = None
        else:
            self._num_gpus = sum([
                len(detail['gpus']) for detail in self._attempts[0]['detail']
            ])
            if self._attempts[0]['start_time'] is None:
                self._run_time = None
                self._queueing_delay = None
            else:
                if self._attempts[-1]['end_time'] is None:
                    self._run_time = None
                else:
                    self._run_time = \
                        philly_utils.timedelta_to_minutes(self._attempts[-1]['end_time'] -
                                             self._attempts[0]['start_time'])
                self._queueing_delay = \
                    philly_utils.timedelta_to_minutes(self._attempts[0]['start_time'] -
                                         self._submitted_time)

    def __repr__(self):
        return (f'Job(job_id={self._jobid},\n'
                f'user={self._user},\n'
                f'status={self._status},\n'
                f'num_gpus = {self._num_gpus},\n'
                f'submitted_time = {self._submitted_time},\n'
                f'run_time={self._run_time}\n'
                f'attempts={self._attempts})')

    @property
    def status(self):
        return self._status

    @property
    def jobid(self):
        return self._jobid

    @property
    def attempts(self):
        return self._attempts

    @property
    def submitted_time(self):
        return self._submitted_time

    @property
    def user(self):
        return self._user

    @property
    def num_gpus(self):
        return self._num_gpus

    @property
    def queueing_delay(self):
        return self._queueing_delay

    @property
    def run_time(self):
        return self._run_time


def load_philly_traces(trace_dir: str):
    print('Loading Philly job trace...')
    trace_dir = os.path.abspath(os.path.expanduser(trace_dir))
    cluster_job_log_path = os.path.join(trace_dir, 'cluster_job_log')
    with open(cluster_job_log_path, 'r') as f:
        cluster_job_log = json.load(f)
    jobs = [
        JobTrace(status=job['status'],
                 jobid=job['jobid'],
                 attempts=job['attempts'],
                 submitted_time=job['submitted_time'],
                 user=job['user']) for job in cluster_job_log
    ]
    jobs = sorted(jobs, key=lambda t: t._submitted_time)
    return jobs
