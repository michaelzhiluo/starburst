import enum
import logging

logger = logging.getLogger(__name__)

STAR_WAIT_THRESHOLD = 300

class WaitingPolicyEnum(enum.Enum):
    """
    Waiting policy types.

    Expressed as w(j)=T, where T is the max waiting time for job j in the
    queue.
    """
    # w(j) = ∞, equivalent to traditional cluster schedulers
    INFINITE = 'infinite'
    # w(j) = 0, equivalent to No-Wait
    ZERO = 'zero'
    # w(j) = waiting_coeff
    CONSTANT = 'constant'
    # w(j) = waiting_coeff * j.runtime
    RUNTIME = 'runtime'
    # w(j) = waiting_coeff * j.resources_requested
    RESOURCE = 'resource'
    # w(j) = waiting_coeff * j.resources_requested * j.runtime
    COMPUTE = 'compute'
    # w(j) = 0 for non preempted jobs, w(j) = 3 * waiting_coeff * j.resources_requested
    STAR = 'star'


class BaseWaitingPolicy(object):
    """
    Base class for waiting policies. Computes the timeout for a job
    based on the policy type.
    """

    def __init__(self, waiting_coeff):
        self.waiting_coeff = waiting_coeff

    def compute_timeout(self, job):
        raise NotImplementedError


class InfiniteWaitingPolicy(BaseWaitingPolicy):

    def compute_timeout(self, job):
        return 1e9


class ConstantWaitingPolicy(BaseWaitingPolicy):

    def compute_timeout(self, job):
        return self.waiting_coeff


class ZeroWaitingPolicy(BaseWaitingPolicy):

    def compute_timeout(self, job):
        # Still wait for 5 seconds to avoid submitting too many jobs to K8 cluster.
        return 5


class RuntimeWaitingPolicy(BaseWaitingPolicy):

    def compute_timeout(self, job):
        runtime = job.runtime
        if runtime is None:
            logger.debug(
                'Job has no runtime estimates; defaulting to 1 hour runtime.')
            runtime = 1
        return self.waiting_coeff * runtime


class StarWaitingPolicy(BaseWaitingPolicy):

    def compute_timeout(self, job):
        resources = job.resources
        if job.preempt:
            if resources['gpu'] == 0:
            # Assume CPU-only workload.
                return 3*self.waiting_coeff * resources['cpu']
            elif resources['gpu'] > 0:
                # Assume GPU-only workload
                return 3*self.waiting_coeff * resources['gpu']
            else:
                raise ValueError(f'Invalid resources requested: {resources}')
        else:
            return 5

class ResourceWaitingPolicy(BaseWaitingPolicy):

    def compute_timeout(self, job):
        resources = job.resources
        if resources['gpu'] == 0:
            # Assume CPU-only workload.
            return self.waiting_coeff * resources['cpu']
        elif resources['gpu'] > 0:
            # Assume GPU-only workload
            return self.waiting_coeff * resources['gpu']
        else:
            raise ValueError(f'Invalid resources requested: {resources}')


class ComputeWaitingPolicy(BaseWaitingPolicy):

    def compute_timeout(self, job):
        resources = job.resources
        runtime = job.runtime
        if runtime is None:
            if 'estimated_runtime' in job.annotations:
                runtime = float(job.annotations['estimated_runtime'])
            else:
                logger.debug(
                    'Job has no runtime estimates; defaulting to 1 hour runtime.')
                runtime = 1
        if resources['gpu'] == 0 or 'gpu' not in resources:
            # Assume CPU-only workload.
            return self.waiting_coeff * resources['cpu'] * runtime
        elif resources['gpu'] > 0:
            # Assume GPU-only workload
            return self.waiting_coeff * resources['gpu'] * runtime
        else:
            raise ValueError(f'Invalid resources requested: {resources}')


def get_waiting_policy_cls(waiting_policy: str):
    """
    Get the waiting policy class based on the policy name.

    Args:
        waiting_policy (str): Name of the waiting policy.
    """
    if (waiting_policy == WaitingPolicyEnum.INFINITE.value
            or not waiting_policy):
        return InfiniteWaitingPolicy
    elif waiting_policy == WaitingPolicyEnum.CONSTANT.value:
        return ConstantWaitingPolicy
    elif waiting_policy == WaitingPolicyEnum.RUNTIME.value:
        return RuntimeWaitingPolicy
    elif waiting_policy == WaitingPolicyEnum.RESOURCE.value:
        return ResourceWaitingPolicy
    elif waiting_policy == WaitingPolicyEnum.COMPUTE.value:
        return ComputeWaitingPolicy
    elif waiting_policy == WaitingPolicyEnum.ZERO.value:
        return ZeroWaitingPolicy
    elif waiting_policy == WaitingPolicyEnum.STAR.value:
        return StarWaitingPolicy
    else:
        raise NotImplementedError(
            f'Waiting policy {waiting_policy} not implemented.')
