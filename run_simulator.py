import argparse
import json

from skyburst import job_gen, run_simulator


def generate_data_run_simulator(run_config):
    proc_jobs = job_gen.load_processed_jobs(
        dataset_config=run_config['jobgen_spec'])

    run_simulator(proc_jobs, run_config)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run a single instantiation of the hybrid cloud simulator.'
    )

    # Arguments for Data Generation
    parser.add_argument("--dataset",
                        type=str,
                        choices=["philly", "philly_gen", "gen_gpu", 'helios'],
                        default='philly',
                        help='Choose dataset to run simulator from.')
    parser.add_argument('--arrival_rate',
                        type=float,
                        default=None,
                        help='Arrival rate for generated jobs.')
    parser.add_argument('--cv_factor',
                        type=float,
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
                        default=64,
                        help='Size of the cluster (i.e. # of cluster nodes)')
    parser.add_argument('--gpus_per_node',
                        type=int,
                        default=8,
                        help='Number of GPU(s) per cluster node')
    parser.add_argument('--cpus_per_node',
                        type=int,
                        default=96,
                        help='Number of CPU(s) per cluster node')

    # Arguments for Policy specifications.
    parser.add_argument(
        '--sched_alg',
        type=str,
        default='fifo',
        help='Scheduling algorithm specifying order of the queue.')
    parser.add_argument('--binpack_alg',
                        type=str,
                        default='first-fit',
                        choices=['first-fit', 'best-fit'],
                        help='Binpacking algorithm for the cluster.')
    parser.add_argument(
        '--waiting_policy',
        type=str,
        default='linear_runtime',
        help='Waiting policy (how long jobs should at max wait in the cloud).')
    parser.add_argument('--backfill',
                        type=int,
                        default=0,
                        choices=[0, 1],
                        help='Enable backfill (assumes time estimator)')
    parser.add_argument(
        '--loop',
        type=int,
        default=0,
        choices=[0, 1],
        help=
        'Enable loop scheduling (just loop through entire queue, remove HoL)')
    parser.add_argument(
        '--predict_wait',
        type=int,
        default=0,
        choices=[0, 1],
        help=
        'Enable prediction. (Jobs predict if they can be assigned to cluster before timing out)'
    )
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

    args = parser.parse_args()
    run_config = {
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
        'predict_wait': args.predict_wait,
        # Simulator config
        'verbose': args.verbose,
        'debug': args.debug,
        'warmup_jobs': args.warmup_jobs,
        'jobgen_spec': {
            'dataset': args.dataset,
            'arrival_rate': args.arrival_rate,
            'cv_factor': args.cv_factor,
            'total_jobs': args.total_jobs,
            'job_runtime': args.job_runtime,
            'seed': args.seed
        }
    }
    generate_data_run_simulator(run_config)
