import argparse
import itertools
import json
import multiprocessing
import pickle
import os

from skyburst import job_gen, run_simulator
from skyburst import utils
from skyburst.filter_config import apply_filter_config


def generate_data_run_simulator(run_config):
    proc_jobs = job_gen.load_processed_jobs(
        dataset_config=run_config['jobgen_spec'])
    return run_simulator(proc_jobs, run_config)


def run_grid_search(run_configs, num_procs=32):
    for i, r in enumerate(run_configs):
        r['pbar_idx'] = i
    run_configs = [[r] for r in run_configs]
    with multiprocessing.Pool(processes=num_procs) as pool:
        results = pool.starmap(generate_data_run_simulator, run_configs)
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=
        'Run a hyperparameter sweep over diff. values in a hybrid cloud simulator.'
    )

    # Arguments for Data Generation
    parser.add_argument("--dataset",
                        type=str,
                        choices=[
                            "philly", "philly_gen", "gen_gpu", "helios",
                            "synthetic", "helios_gen"
                        ],
                        default='philly',
                        help='Choose dataset to run simulator from.')
    parser.add_argument('--arrival_rate',
                        type=float,
                        nargs='+',
                        default=None,
                        help='Arrival rate for generated jobs.')
    parser.add_argument('--cv_factor',
                        type=float,
                        nargs='+',
                        default=1.0,
                        help='Varies job burstiness.')
    parser.add_argument('--total_jobs',
                        type=int,
                        default=None,
                        help='How many jobs should be generated.')
    parser.add_argument('--job_runtime',
                        type=float,
                        default=4.0,
                        help='Average runtime for job.')

    # Arguments for Cluster specifications.
    parser.add_argument('--cluster_size',
                        type=int,
                        nargs='+',
                        default=64,
                        help='Size of the cluster (i.e. # of cluster nodes)')
    parser.add_argument('--gpus_per_node',
                        type=int,
                        default=8,
                        help='Number of GPU(s) per cluster node')
    parser.add_argument('--cpus_per_node',
                        type=int,
                        default=48,
                        help='Number of CPU(s) per cluster node')

    # Arguments for Policy specifications.
    parser.add_argument(
        '--sched_alg',
        type=str,
        nargs='+',
        default='fifo',
        help='Scheduling algorithm specifying order of the queue.')
    parser.add_argument('--binpack_alg',
                        type=str,
                        nargs='+',
                        default='first-fit',
                        choices=['first-fit', 'best-fit', 'worst-fit'],
                        help='Binpacking algorithm for the cluster.')
    parser.add_argument(
        '--waiting_policy',
        type=str,
        nargs='+',
        default='linear_runtime',
        help='Waiting policy (how long jobs should at max wait in the cloud).')
    parser.add_argument('--clip_time',
                        type=float,
                        default=1e9,
                        nargs='+',
                        help='Sets maximum clipping time for a job.')
    parser.add_argument('--backfill',
                        type=int,
                        nargs='+',
                        default=0,
                        choices=[0, 1],
                        help='Enable backfill (assumes time estimator)')
    parser.add_argument(
        '--loop',
        type=int,
        nargs='+',
        default=0,
        choices=[0, 1],
        help=
        'Enable loop scheduling (just loop through entire queue, remove HoL)')
    parser.add_argument(
        '--predict_wait',
        type=int,
        nargs='+',
        default=0,
        choices=[0, 1, 2],
        help=
        'Enable prediction. (Jobs predict if they can be assigned to cluster before timing out)'
    )
    parser.add_argument('--time_estimator_error',
                        type=int,
                        nargs='+',
                        default=0,
                        help='Time estimator error')
    parser.add_argument('--max_queue_length',
                        type=int,
                        default=-1,
                        nargs='+',
                        help='Sets maximum length for queue.')

    parser.add_argument(
        '--long_job_thres',
        type=float,
        nargs='+',
        default=-1,
        help='Long job threshold (if lower than threshold move to cloud).')
    parser.add_argument('--preempt_cloud_ratio',
                        type=float,
                        nargs='+',
                        default=-1,
                        help='Cloud preemption threshold.')
    parser.add_argument('--data_gravity',
                        type=float,
                        nargs='+',
                        default=-1,
                        help='Data gravity delay for running in the cloud.')

    parser.add_argument('--seed',
                        type=int,
                        default=2024,
                        help='Seed for data generation.')
    parser.add_argument('--verbose',
                        action='store_true',
                        help='Prints out simulator state at every timestep')
    parser.add_argument('--debug',
                        action='store_true',
                        help='Appends python debugger at every timestemp')
    parser.add_argument(
        '--warmup_jobs',
        type=int,
        default=5000,
        help=
        'Jobs to not consider for final metrics at the beg. and end. of simulator'
    )
    parser.add_argument(
        '--filter_name',
        type=str,
        default=None,
        help='Specifies filter config.')
    parser.add_argument(
        '--log',
        type=str,
        default=None,
        help='Specifies where to save the simulator sweep results.')

    parser.add_argument(
        '--snapshot',
        type=int,
        default=0,
        choices=[0, 1],
        help=
        'Specifies whether to save queue state at the end of each iteration. (This is used for underutilization analysis.)'
    )

    args = parser.parse_args()
    grid_search_config = {
        # Cluster config
        'cluster_size': args.cluster_size,
        'gpus_per_node': args.gpus_per_node,
        'cpus_per_node': args.cpus_per_node,
        # Policy config
        'sched_alg': args.sched_alg,
        'binpack_alg': args.binpack_alg,
        'waiting_policy': args.waiting_policy,
        'backfill': args.backfill,
        'loop': args.loop,
        'clip_time': args.clip_time,
        'predict_wait': args.predict_wait,
        'long_job_thres': args.long_job_thres,
        'preempt_cloud_ratio': args.preempt_cloud_ratio,
        'data_gravity': args.data_gravity,
        # Simulator config
        'verbose': args.verbose,
        'debug': args.debug,
        'warmup_jobs': args.warmup_jobs,
        'snapshot': args.snapshot,
        'max_queue_length': args.max_queue_length,
        'time_estimator_error': args.time_estimator_error,
        'jobgen_spec': {
            'dataset': args.dataset,
            'arrival_rate': args.arrival_rate,
            'cv_factor': args.cv_factor,
            'total_jobs': args.total_jobs,
            'job_runtime': args.job_runtime,
            'seed': args.seed
        }
    }
    grid_search_config = utils.convert_to_lists(grid_search_config)
    run_configs = utils.generate_cartesian_product(grid_search_config)
    run_configs = apply_filter_config(args.filter_name, run_configs)

    final_simulator_results = run_grid_search(run_configs)
    if args.log:
        file_path = args.log
    else:
        file_path = None
    if args.log:
        absolute_file_path = os.path.abspath(file_path)
        dir_path = os.path.dirname(absolute_file_path)
        os.system(f'mkdir -p {dir_path}')
        file = open(absolute_file_path, 'wb')
        pickle.dump(final_simulator_results, file)
        file.close()
