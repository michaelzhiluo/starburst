from typing import Callable

from utils import parse_date, timedelta_to_minutes


class Job:
    """Encapsulates a job."""
    def __init__(self,
                 status,
                 vc,
                 jobid,
                 attempts,
                 submitted_time,
                 user: str = None):
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
               vc: The hash of the virtual cluster id the job was run in.
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
        self._vc = vc
        self._jobid = jobid
        for attempt in attempts:
            attempt['start_time'] = parse_date(attempt['start_time'])
            attempt['end_time'] = parse_date(attempt['end_time'])
        self._attempts = attempts
        self._submitted_time = parse_date(submitted_time)
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
                        timedelta_to_minutes(self._attempts[-1]['end_time'] -
                                             self._attempts[0]['start_time'])
                self._queueing_delay = \
                    timedelta_to_minutes(self._attempts[0]['start_time'] -
                                         self._submitted_time)

    @property
    def status(self):
        return self._status

    @property
    def vc(self):
        return self._vc

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
