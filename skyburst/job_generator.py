import numpy as np
from typing import Any, Dict, List

from skyburst import Job, waiting_policy
from skyburst.traces import philly


# Returns the total cost of a GPU-only job.
def gpu_cost_fn(resources: dict, runtime: float):
    return resources['GPUs'] * runtime


# Returns the total cost of a GPU/CPU hybrid job.
def hybrid_cost_fn(resources: dict, runtime: float):
    return 50 * resources['GPUs'] * runtime + resources['CPUs'] * runtime


def load_processed_jobs(dataset_config: Dict[str, Any]):
    dataset_type = dataset_config['dataset']
    if dataset_type == 'philly':
        philly_jobs = philly.load_philly_traces('~/philly-traces/trace-data')
        return process_philly_jobs(philly_jobs)
    elif dataset_type == 'philly_gen':
        philly_jobs = philly.load_philly_traces('~/philly-traces/trace-data')
        dataset_kwargs = {
            'total_jobs': dataset_config['total_jobs'],
            'arrival_rate': dataset_config['arrival_rate'],
            'cv_factor': dataset_config['cv_factor'],
            'seed': dataset_config['seed'],
        }
        return generate_philly_gpu_jobs(philly_jobs, **dataset_kwargs)
    elif dataset_type == 'gen_gpu':
        philly_jobs = philly.load_philly_traces('~/philly-traces/trace-data')
        dataset_kwargs = {
            'total_jobs': dataset_config['total_jobs'],
            'arrival_rate': dataset_config['arrival_rate'],
            'job_runtime': dataset_config['job_runtime'],
            'seed': dataset_config['seed'],
        }
        return generate_gpu_jobs(philly_jobs, **dataset_kwargs)
    else:
        raise ValueError(
            f'Dataset {dataset_type} does not exist or has not been implemented yet.'
        )


def process_philly_jobs(philly_jobs: List['JobTrace']):
    """Converts entire Philly job trace into a list of simulator jobs.
    """
    jobs = philly_jobs.copy()
    # Remove invalid jobs (jobs that have not finished and jobs that failed/killed early)
    jobs = [j for j in jobs if j._run_time is not None and j.status == 'Pass']
    jobs.sort(key=lambda j: j._submitted_time)

    # Arrival time for jobs
    start_time = jobs[0]._submitted_time
    arrival_times = [(j._submitted_time - start_time).total_seconds() / 3600.0
                     for j in jobs]

    # Run time for jobs
    run_times = [j._run_time / 60.0 for j in jobs]

    # Get GPU resources
    resources = []
    for j in jobs:
        gpu_count = sum(
            [len(node_dict['gpus']) for node_dict in j.attempts[-1]['detail']])
        resources.append({'GPUs': gpu_count})

    costs = [res['GPUs'] * run for res, run in zip(resources, run_times)]

    return [Job(idx, arrival=arr, runtime=run, resources=res, cost=cost) \
            for idx, (arr, run, res, cost) in \
            enumerate(list(zip(arrival_times, run_times, resources, costs)))]


def generate_philly_gpu_jobs(philly_jobs: List['JobTrace'],
                             arrival_rate=32.0,
                             cv_factor=1.0,
                             total_jobs=200000,
                             seed=2024):
    """Generates Philly jobs based on a Poisson arrival distribution.

    Interarrival times follow an exponential distribution of 1/arrival_rate.
    Jobs are randomly sampled from the Philly job trace.
    """
    total_jobs = int(total_jobs)
    jobs = philly_jobs.copy()
    # Remove invalid jobs (jobs that have not finished and jobs that failed/killed early)
    jobs = [j for j in jobs if j._run_time is not None and j.status == 'Pass']
    jobs.sort(key=lambda j: j._submitted_time)

    # Arrival time for jobs
    np.random.seed(seed)
    alpha = (1.0 / cv_factor)**2
    interarrival_times = np.array([
        np.random.gamma(shape=alpha, scale=1 / (alpha * arrival_rate))
        for _ in range(total_jobs - 1)
    ])
    print(np.mean(interarrival_times))
    exit(0)
    # interarrival_times = np.random.exponential(scale=1 / arrival_rate,
    #                                            size=total_jobs - 1)
    interarrival_times = np.insert(interarrival_times, 0, 0)
    arrival_times = np.cumsum(interarrival_times)

    # Run time for jobs
    run_times = []
    for j in jobs:
        run_time_hr = j._run_time / 60.0
        run_times.append(run_time_hr)

    # Get GPU resources
    resources = []
    for j in jobs:
        detail_dict = j.attempts[-1]['detail']
        gpu_count = sum([len(node_dict['gpus']) for node_dict in detail_dict])
        resources.append({'GPUs': gpu_count})
    np.random.seed(seed)
    job_indexes = np.random.choice(list(range(len(run_times))),
                                   size=total_jobs,
                                   replace=True)
    proc_jobs = []
    for idx in range(total_jobs):
        job_idx = job_indexes[idx]
        resources_dict = resources[job_idx]
        runtime = run_times[job_idx]
        cost = resources_dict['GPUs'] * runtime
        proc_jobs.append(
            Job(idx,
                arrival=arrival_times[idx],
                runtime=runtime,
                resources=resources_dict,
                cost=cost))
    return proc_jobs


def generate_gpu_jobs(philly_jobs: List['JobTrace'],
                      arrival_rate=32.0,
                      job_runtime=4.0,
                      total_jobs=200000,
                      seed=2024):
    """Generates GPU jobs based on a Poisson arrival distribution and exponential runtime distribution.
    """
    total_jobs = int(total_jobs)
    jobs = philly_jobs.copy()
    # Remove invalid jobs (jobs that have not finished and jobs that failed/killed early)
    jobs = [j for j in jobs if j._run_time is not None and j.status == 'Pass']
    jobs.sort(key=lambda j: j._submitted_time)

    # Arrival time for jobs
    np.random.seed(seed)
    interarrival_times = np.random.exponential(scale=1 / arrival_rate,
                                               size=total_jobs - 1)
    interarrival_times = np.insert(interarrival_times, 0, 0)
    arrival_times = np.cumsum(interarrival_times)

    # Run time for jobs
    run_times = np.random.exponential(scale=job_runtime, size=total_jobs)

    # Get GPU resources
    resources = []
    for j in jobs:
        detail_dict = j.attempts[-1]['detail']
        gpu_count = sum([len(node_dict['gpus']) for node_dict in detail_dict])
        resources.append({'GPUs': gpu_count})
    np.random.seed(seed)
    job_indexes = np.random.choice(list(range(len(resources))),
                                   size=total_jobs,
                                   replace=True)
    proc_jobs = []
    for idx in range(total_jobs):
        job_idx = job_indexes[idx]
        runtime = run_times[idx]
        resources_dict = resources[job_idx]
        cost = resources_dict['GPUs'] * runtime
        proc_jobs.append(
            Job(idx,
                arrival=arrival_times[idx],
                runtime=runtime,
                resources=resources_dict,
                cost=cost))
    return proc_jobs
