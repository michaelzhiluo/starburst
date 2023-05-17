import copy
import numpy as np
from typing import Any, Dict, List, Optional

from tabulate import tabulate
from tqdm import tqdm

from skyburst import Cluster, Job, utils, waiting_policy

DEFAULT_SIMULATOR_SPEC = {
    # Size of the cluster (i.e. # of cluster nodes).
    'cluster_size': 64,
    # Number of GPU(s) per cluster node.
    'gpus_per_node': 8,
    # Number of CPU(s) per cluster node.
    'cpus_per_node': 96,
    # Scheduling algorithm specifying order of the queue.
    'sched_alg': 'fifo',
    # How jobs are binpacked into the cluster.
    'binpack_alg': 'first-fit',
    # Waiting policy (how long jobs should wait in the cloud).
    'waiting_policy': 'linear_runtime',
    # Waiting hyperparameter (to be passed to waiting_policy)
    'waiting_factor': 1.25,
    # Sets clipping time for waiting (max time a job should wait)
    'clip_time': 1e9,
    # Enable backfill (assumes time estimator).
    'backfill': False,
    # Enable loop scheduling (just loop through entire queue, remove HoL).
    'loop': False,
    # Enable prediction. (Jobs predict if they can be assigned to cluster before timing out).
    # 0 is no prediction, 1 is perfect oracle
    'predict_wait': 0,
    # Queue length
    'max_queue_length': -1,
    # Time estimator error
    'time_estimator_error': 0,
    # (Deprecated) Algorithm to immediately send job to cloud (without waiting).
    'filter_alg': None,
    # Prints out simulator state at every timestep.
    'verbose': False,
    # Appends python debugger at every timestemp.
    'debug': False,
    # Position for TQDM progress tracker bar.
    'pbar_idx': 0,
    # Jobs to not consider for final metrics at the beg. and end. of simulator.
    'warmup_jobs': 5000,
    # Whether to get snapshots and save to result dict
    'snapshot': False,
    # Metadata on job generation (run prior to simulator).
    'jobgen_spec': {
        # Dataset type ['philly', 'philly_gen', 'gen_gpu']
        'dataset': 'philly',
        # Arrival rate of jobs (used in 'gen_gpu', 'philly_gen')
        'arrival_rate': -1,
        # Total number of jobs generated.
        'total_jobs': -1,
        # Avg. Job runtime (used in 'gen_gpu')
        'job_runtime': -1,
    }
}


def run_simulator(
        jobs: List[Job],
        simulator_spec: Optional[Dict[str, Any]] = DEFAULT_SIMULATOR_SPEC):
    """Executes a simulator over a fixed set of jobs. Returns a 
    a result dictionary over all finished jobs.

    Args:
        jobs: List of generated jobs sorted by their arrival times.
        simulator_spec: Simulator settings, see above dictionary for default
                        values.
    """
    _simulator_spec = DEFAULT_SIMULATOR_SPEC.copy()
    _simulator_spec.update(simulator_spec)
    simulator_spec = _simulator_spec

    sched_alg = simulator_spec['sched_alg']
    sort_func = utils.generate_sorting_function(sched_alg)

    waiting_policy_str = simulator_spec['waiting_policy'].split('-')
    assert len(waiting_policy_str) <= 2
    if len(waiting_policy_str) == 2:
        simulator_spec['waiting_policy'] = waiting_policy_str[0]
        simulator_spec['waiting_factor'] = float(waiting_policy_str[1])

    waiting_fn = waiting_policy.lookup_linear_function(
        simulator_spec['waiting_policy'],
        waiting_factor=simulator_spec['waiting_factor'])
    binpack_alg = simulator_spec['binpack_alg']
    backfill = simulator_spec['backfill']
    loop = simulator_spec['loop']
    predict_wait = simulator_spec['predict_wait']
    clip_time = simulator_spec['clip_time']
    filter_alg = simulator_spec['filter_alg']
    max_queue_length = simulator_spec['max_queue_length']
    time_estimator_error = simulator_spec['time_estimator_error'] / 100.0
    assert not (
        backfill and loop
    ), f'Must only set one option to be True - backfill:{backfill}, loop:{loop} '

    verbose = simulator_spec['verbose']
    debug = simulator_spec['debug']
    snapshot = simulator_spec['snapshot']
    # Initialize simulator variables\
    jobs = copy.deepcopy(jobs)
    queue = []
    finished_jobs = []
    num_jobs = len(jobs)
    cloud_cost = 0.0
    # Create fake cluster. The cluster is homogeneous.
    cluster = Cluster(num_nodes=simulator_spec['cluster_size'],
                      num_gpus_per_node=simulator_spec['gpus_per_node'],
                      num_cpus_per_node=simulator_spec['cpus_per_node'],
                      backfill=backfill,
                      binpack=binpack_alg)
    t = 0
    pbar = tqdm(total=len(jobs),
                desc="Jobs progress: ",
                position=simulator_spec['pbar_idx'])

    snapshots = {}

    total_local_wait = 0
    total_finished_local_jobs = 0
    total_cloud_jobs = 0

    queue_length = []
    prev_t = -1
    while len(jobs) > 0 or len(queue) > 0 or cluster.active_jobs:
        # Clear cluster of jobs that have completed
        completed_jobs = cluster.try_clear(t)
        finished_jobs.extend(completed_jobs)

        # Check for jobs that have waited too long (move to cloud).
        i = 0
        while i < len(queue):
            job = queue[i]
            # If job has timed out, send to cloud.
            if t >= job.deadline - job.runtime:
                queue.remove(job)
                job.state = 'TIMEOUT-CLOUD'
                # Shortcut: Job can predict it will go to cloud or not, if so, it would have began running at job.arrival.
                # Perfect Oracle
                if predict_wait == 1:
                    job.start = job.arrival
                elif predict_wait == 0 or predict_wait == 2:
                    job.start = job.deadline - job.runtime
                else:
                    raise ValueError(
                        f'Predict wait {predict_wait} wrong value!')
                cloud_cost += job.cost
                total_cloud_jobs += 1
                finished_jobs.append(job)
            else:
                i += 1

        # Add jobs to queue that have arrived. Jobs are assumed to have been ordered by arrival times.
        i = 0
        while i < len(jobs):
            job = jobs[i]
            if job.arrival < t:
                raise ValueError("Should not have entered here!")
            elif job.arrival == t:
                jobs.remove(job)
                deadline = waiting_fn(job)
                job.set_deadline(deadline)
                if deadline == -1:
                    job.state = 'TIMEOUT-CLOUD'
                    job.start = job.arrival
                    job.set_deadline(deadline=job.arrival + job.runtime)
                    cloud_cost += job.cost
                    finished_jobs.append(job)
                else:
                    if time_estimator_error != 0:
                        original_runtime = job.runtime
                        mod_runtime = original_runtime + np.random.normal(
                            loc=0.0,
                            scale=time_estimator_error * original_runtime)
                        mod_runtime = max(0, mod_runtime)
                        if simulator_spec[
                                'waiting_policy'] == 'linear_cost_filter_cpu':
                            deadline = job.arrival + simulator_spec[
                                'waiting_factor'] * (
                                    job.resources['GPUs'] +
                                    job.resources['CPUs'] /
                                    53.0) * mod_runtime + job.runtime
                    waiting_time = max(0.0,
                                       deadline - job.runtime - job.arrival)
                    if waiting_time < 0:
                        raise ValueError('wtf bbq')
                    waiting_time = min(clip_time, waiting_time)
                    job.set_deadline(deadline=job.arrival + job.runtime +
                                     waiting_time)
                    queue_length.append(len(queue))
                    queue.append(job)
                pbar.update(1)
            else:
                break

        # Sort the queue based on the scheduling algorithm.
        queue.sort(key=sort_func)

        # Go through queue and fit jobs onto cluster as needed
        preempted_jobs = []
        i = 0
        while i < len(queue):
            job = queue[i]
            can_fit, preempted_jobs = cluster.try_fit_v2(t, job)
            if can_fit:
                queue.remove(job)
                #queue.extend(preempted_jobs)
            elif not loop:
                break
            else:
                i += 1

        # Perform EASY backfilling (assumes time estimator)
        if backfill:
            # Reserve the first element of queue that is blocking
            if queue:
                job_to_reserve = queue[0]
                can_reserve = cluster.try_reserve(t, job_to_reserve)
                # If can't reserve within reasonble time, leave the job in the queue.
                if not can_reserve:
                    pass
                else:
                    queue.remove(job_to_reserve)
                i = 0
                while i < len(queue):
                    job = queue[i]
                    can_fit, preempted_jobs = cluster.try_fit_v2(t, job)
                    if can_fit:
                        queue.remove(job)
                        #queue.extend(preempted_jobs)
                    else:
                        i += 1

        if max_queue_length != -1:
            while len(queue) > max_queue_length:
                q_job = queue[-1]
                queue.remove(q_job)
                q_job.state = 'TIMEOUT-CLOUD'
                q_job.start = t
                q_job.set_deadline(deadline=q_job.arrival + q_job.runtime)
                cloud_cost += q_job.cost
                finished_jobs.append(q_job)

        if snapshot:
            if t not in snapshots:
                snapshots[t] = {}
            snapshots[t]['new_queue'] = copy.deepcopy(queue)

        next_time_list = []

        # Skip to next timestep where a new job either arrives or when a job finishes on the cluster.
        for job_idx, job in cluster.active_jobs.items():
            next_time_list.append(job.start + job.runtime)

        if len(jobs) > 0:
            next_time_list.append(jobs[0].arrival)

        # If there are no jobs left in the cluster and in the job and queue, terminate simulation.
        if len(next_time_list) == 0:
            assert len(queue) == 0 and len(jobs) == 0
            break

        if min(next_time_list) < t:
            raise ValueError(
                f'Simulator cannot go back in time: {t}->{min(next_time_list)}'
            )

        t = min(next_time_list)

        if verbose or debug:
            headers = [
                'Timestamp', 'Cloud Cost', 'Queue Length', 'Jobs Left',
                'Finished Jobs'
            ]
            data = [(t, cloud_cost, len(queue), len(jobs), len(finished_jobs))]
            print(tabulate(data, headers=headers))
            if debug:
                import pdb
                pdb.set_trace()

    end_sim_jobs = cluster.try_clear(1e12)
    assert len(end_sim_jobs) == 0 and len(jobs) == 0 and len(
        queue) == 0, 'Simulator did not finish properly.'
    finished_jobs.sort(key=lambda x: x.idx)

    # Generate final logs for the simulator.
    result_dict = {
        'idx': np.array([j.idx for j in finished_jobs]),
        'arrival': np.array([j.arrival for j in finished_jobs]),
        'start': np.array([j.start for j in finished_jobs]),
        'runtime': np.array([j.runtime for j in finished_jobs]),
        'deadline': np.array([j.deadline for j in finished_jobs]),
        'num_gpus': np.array([j.num_gpus for j in finished_jobs]),
        'state': np.array([j.state for j in finished_jobs]),
        'allocated_gpus': np.array([j.allocated_gpus for j in finished_jobs]),
        'simulator_spec': simulator_spec,
        'stats': {}
    }

    if snapshot:
        result_dict['snapshot'] = snapshots
    # Computing Simulator stats, such as avg. waiting, avg. JCT, cloud cost, utilization.
    total_waiting_time = 0.0
    total_running_time = 0.0
    num_jobs = 0
    total_cloud_cost = 0
    sum_local_space = 0.0
    sum_cloud_space = 0.0

    start_time = finished_jobs[simulator_spec['warmup_jobs']].arrival
    end_time = finished_jobs[len(finished_jobs) -
                             simulator_spec['warmup_jobs'] - 1].arrival

    for job in finished_jobs:
        inter_start = max(job.start, start_time)
        inter_end = min(job.start + job.runtime, end_time)
        # Cut off beginning and ending of simulator to reach steady state.
        if job.idx < simulator_spec['warmup_jobs'] or job.idx > len(
                finished_jobs) - simulator_spec['warmup_jobs']:
            if job.state == 'LOCAL':
                if inter_end >= inter_start:
                    sum_local_space += job.num_gpus * (inter_end - inter_start)
            elif job.state == 'TIMEOUT-CLOUD':
                if inter_end >= inter_start:
                    sum_cloud_space += job.num_gpus * (inter_end - inter_start)
            continue
        # Moved to cloud
        if job.state == 'TIMEOUT-CLOUD':
            total_waiting_time += job.start - job.arrival
            if inter_end >= inter_start:
                sum_cloud_space += job.num_gpus * (inter_end - inter_start)
            total_cloud_cost += job.cost
        elif job.state == 'LOCAL':
            total_waiting_time += job.start - job.arrival
            if inter_end >= inter_start:
                sum_local_space += job.num_gpus * (inter_end - inter_start)
        total_running_time += job.runtime
        num_jobs += 1

    result_dict['stats']['total_cloud_cost'] = total_cloud_cost
    result_dict['stats']['avg_cloud_cost'] = total_cloud_cost / (end_time -
                                                                 start_time)
    result_dict['stats']['avg_waiting'] = total_waiting_time / num_jobs
    result_dict['stats']['avg_jct'] = (total_waiting_time +
                                       total_running_time) / num_jobs
    result_dict['stats']['cluster_utilization'] = sum_local_space / (
        simulator_spec['cluster_size'] * simulator_spec['gpus_per_node'] *
        (end_time - start_time))
    result_dict['stats']['system_utilization'] = (
        sum_local_space + sum_cloud_space) / (simulator_spec['cluster_size'] *
                                              simulator_spec['gpus_per_node'] *
                                              (end_time - start_time))

    stats_dict = result_dict['stats']
    headers = [
        'Sched Policy', 'Waiting Policy', '# Cluster Nodes',
        'Total Cloud Cost', 'Avg. Cloud Cost', 'Avg. Waiting', 'Avg. JCT',
        'Cluster Utilization', 'System Utilization'
    ]
    waiting_policy_str = simulator_spec['waiting_policy']
    waiting_factor_str = simulator_spec['waiting_factor']
    data = [(simulator_spec['sched_alg'], \
        f'{waiting_policy_str}-{waiting_factor_str}', simulator_spec['cluster_size'], \
        stats_dict['total_cloud_cost'], stats_dict['avg_cloud_cost'], \
        stats_dict['avg_waiting'], stats_dict['avg_jct'], stats_dict['cluster_utilization'], stats_dict['system_utilization'])]
    print(tabulate(data, headers=headers))
    # import pdb
    # pdb.set_trace()
    return result_dict
