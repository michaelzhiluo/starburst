import numpy as np

from skyburst import Job


def lookup_linear_function(func_type, waiting_factor=1):
    if func_type == 'constant':
        return lambda x: deadline_constant_fn(x, waiting_factor=waiting_factor)
    elif func_type == 'zero':
        return deadline_zero_fn
    elif func_type == 'infinite':
        return deadline_infinite_fn
    elif func_type == 'linear_runtime':
        return lambda x: deadline_linear_runtime_fn(
            x, waiting_factor=waiting_factor)
    elif func_type == 'linear_runtime_filter_cpu':
        return lambda x: deadline_linear_runtime_filter_cpu_fn(
            x, waiting_factor=waiting_factor)
    elif func_type == 'linear_runtime_cap':
        return lambda x: deadline_linear_runtime_cap_fn(
            x, waiting_factor=waiting_factor)
    elif func_type == 'linear_capacity':
        return lambda x: deadline_linear_capacity_fn(
            x, waiting_factor=waiting_factor)
    elif func_type == 'log_capacity':
        return lambda x: deadline_log_capacity_fn(
            x, waiting_factor=waiting_factor)
    elif func_type == 'quad_capacity':
        return lambda x: deadline_quad_capacity_fn(
            x, waiting_factor=waiting_factor)
    elif func_type == 'linear_cost':
        return lambda x: deadline_linear_cost_fn(x,
                                                 waiting_factor=waiting_factor)
    else:
        raise ValueError(f'Waiting policy {func_type} does not exist.')


# Cluster Scheduling (there is no cloud).
def deadline_infinite_fn(job: Job, waiting_factor=1):
    return 1e12


# Cluster Autoscaling (there is no waiting time).
def deadline_zero_fn(job: Job, waiting_factor=1):
    return job.arrival + job.runtime


# Constant Waiting Policy, all jobs wait for `wait_time` before moving to cloud.
def deadline_constant_fn(job: Job, waiting_factor=1):
    return job.arrival + waiting_factor + job.runtime


# Linear Waiting policy, all jobs wait as a linear function of their runtimes.
def deadline_linear_runtime_fn(job: Job, waiting_factor=1.25):
    waiting_time = (waiting_factor - 1) * job.runtime
    waiting_time = max(1 / 12.0, waiting_time)
    return job.arrival + waiting_time + job.runtime


# Linear Waiting policy, all jobs wait as a linear function of their runtimes.
def deadline_linear_runtime_filter_cpu_fn(job: Job, waiting_factor=1.25):
    if job.resources['GPUs'] == 0:
        return -1
    waiting_time = (waiting_factor - 1) * job.runtime
    waiting_time = max(1 / 12.0, waiting_time)
    return job.arrival + waiting_time + job.runtime


# Linear Waiting policy, but waiting times are capped between 5 min, and 48 hours.
def deadline_linear_runtime_cap_fn(job: Job, waiting_factor=1.25):
    waiting_time = (waiting_factor - 1) * job.runtime
    waiting_time = min(48, max(1 / 12.0, waiting_time))
    return job.arrival + waiting_time + job.runtime


# Jobs wait as a linear function of resource request.
def deadline_linear_capacity_fn(job: Job, waiting_factor=1):
    return job.arrival + waiting_factor * job.resources['GPUs'] + job.runtime


# Jobs wait as a quadratic function of resource request.
def deadline_quad_capacity_fn(job: Job, waiting_factor=1):
    return job.arrival + waiting_factor * (job.resources['GPUs']**
                                           2) + job.runtime


# Jobs wait as a log function of resource request.
def deadline_log_capacity_fn(job: Job, waiting_factor=1):
    num_gpus = job.resources['GPUs']
    if num_gpus == 0:
        return job.arrival + job.runtime
    return job.arrival + waiting_factor * (1 + np.log2(num_gpus)) + job.runtime


def deadline_linear_cost_fn(job: Job, waiting_factor=1):
    return job.arrival + waiting_factor * job.cost + job.runtime


# Jobs wait as a function of its surface area (resource * runtime).
def deadline_linear_area_fn(job: Job, waiting_factor=1):
    return job.arrival + waiting_factor * job.resources[
        'GPUs'] * job.runtime + job.runtime
