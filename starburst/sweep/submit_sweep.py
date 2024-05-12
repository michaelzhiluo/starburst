import argparse
import copy
import itertools
import logging
import multiprocessing as mp
import os
import psutil
import time
from typing import List

import starburst.drivers.main_driver as driver
from starburst.sweep import job_generator, utils
from starburst.sweep.services import job_submission, event_logger

DEFAULT_CONFIG_PATH = 'default.yaml'
LOG_DIRECTORY = "../sweep_logs/{name}/"

logger = logging.getLogger(__name__)


def clear_prior_sweeps(retry_limit: int = 1) -> None:
    """
    Deletes all prior sweeps from the cluster.

    Args:
        retry_limit (int): Number of times to retry deleting a sweep 
                           before giving up.
    """
    current_pid = os.getpid()
    for _ in range(retry_limit):
        # Get a list of all processes.
        processes = psutil.process_iter()
        found_submit_process = False
        for process in processes:
            try:
                # Obtain process name and CMD line arguments.
                name = process.name()
                cmdline = process.cmdline()
                # Check for prior sweeps and if the prior sweep is not this
                # current sweep.
                if (name == "python3" and "submit_jobs.py" in cmdline
                        and process.pid != current_pid):
                    # terminate the process
                    process.terminate()
                    found_submit_process = True
            except (psutil.NoSuchProcess, psutil.AccessDenied,
                    psutil.ZombieProcess):
                pass
        if not found_submit_process:
            break


def generate_runs(sweep_config: dict) -> List[dict]:
    """
    Takes specified sweep config and generates grid of runs.

    Args:
        sweep_config (dict): Dictionary of hyperparameters to sweep over.
    """
    list_type_args = ["cpu_sizes", "cpu_dist", "gpu_sizes", "gpu_dist"]

    # Split sweep_config into fixed and varied hyperparameters.
    base_config = utils.load_yaml_file(DEFAULT_CONFIG_PATH)
    varied_config = {}
    for key, value in sweep_config.items():
        if not isinstance(value, list):
            base_config[key] = value
        elif (isinstance(value, list) and key in list_type_args
              and not isinstance(value[0], list)):
            base_config[key] = value
        else:
            varied_config[key] = value

    # Generate carteisan production across varied hyperparameters.
    keys = []
    values = []
    for key, value in varied_config.items():
        keys.append(key)
        values.append(value)
    grid_search = itertools.product(*values)

    # Generate runs from cartesian product.
    runs = {}
    for run_index, trial in enumerate(grid_search):
        for key_index, key in enumerate(keys):
            base_config[key] = trial[key_index]
        runs[run_index] = copy.deepcopy(base_config)
    return runs


def launch_run(run_config: dict, sweep_name: str, run_index: int = 0):
    """
    Launches a single run of the sweep.

    Description:
        1) Generates jobs for the run.
        2) Clears the cluster of any prior jobs.
        3) Launches the scheduler, event logger, and job submission services.

    Args:
        run_config (dict): Dictionary of run hyperparameters.
        sweep_name (str): Name of sweep.
        run_index (int): Index of run.
    """
    run_config = utils.RunConfig(run_config)

    # Generate jobs and their corresponding arrival times.
    jobs = job_generator.generate_jobs(sweep_name=sweep_name,
                                       run_config=run_config)
    job_yaml_path = (f"{LOG_DIRECTORY.format(name=sweep_name)}"
                     f"jobs/{run_index}.yaml")
    utils.save_yaml_object(jobs, job_yaml_path)

    while not utils.check_empty_cluster(clusters=run_config.clusters):
        logger.debug("Cleaning cluster pods, jobs, and event logs...")
        utils.clear_clusters(clusters=run_config.clusters)
        time.sleep(1)
    logger.debug(f"Starting Run ID: {run_index}.")

    waiting_budget = run_config.waiting_budget
    waiting_coeff = run_config.waiting_coeff
    if waiting_budget != -1:
        waiting_coeff = utils.estimate_waiting_coeff(run_config.waiting_policy,
                                                     run_config.waiting_budget,
                                                     jobs)
    policy_config = {
        'waiting_policy': run_config.waiting_policy,
        'waiting_coeff': waiting_coeff,
        'queue_policy': run_config.queue_policy,
        'loop': run_config.loop,
        'min_waiting_time': run_config.min_waiting_time,
    }
    run_config.clusters['cloud']['log_file'] = (
        f'{LOG_DIRECTORY.format(name=sweep_name)}/events/'
        f'{run_index}.log')

    policy_config['schedule_tick'] = run_config.schedule_tick

    scheduler_service = mp.Process(
        target=driver.launch_starburst_scheduler,
        args=(
            driver.GRPC_PORT,
            run_config.clusters,
            policy_config,
        ),
    )
    scheduler_service.start()

    event_logger_service = mp.Process(
        target=event_logger.logger_service,
        args=(
            run_config.clusters,
            jobs,
            sweep_name,
            run_index,
        ),
    )
    event_logger_service.start()

    job_submission_service = mp.Process(
        target=job_submission.job_submission_service,
        args=(jobs, run_config.clusters, sweep_name, run_index),
    )
    job_submission_service.start()

    job_submission_service.join()

    event_logger_service.terminate()
    event_logger_service.join()
    scheduler_service.terminate()
    scheduler_service.join()
    logger.debug("Sweep complete.")


def sweep_pipeline(sweep_config: str):
    """
    Runs a hyperparameter sweep on the cluster.

    Args:
        sweep_config (str): Path to YAML file containing sweep configuration.
    """
    # 1) Clean Sweeps from prior runs.
    clear_prior_sweeps(retry_limit=3)

    # 2) Create Log directory for sweep
    cur_time = int(time.time())
    log_directory_path = LOG_DIRECTORY.format(name=str(cur_time))
    utils.create_log_directory(LOG_DIRECTORY.format(name=log_directory_path))

    # 3) Load sweep config and generate runs.
    sweep_dict = utils.load_yaml_file(sweep_config)
    runs_dict = generate_runs(sweep_dict)
    utils.save_yaml_object(runs_dict, f"{log_directory_path}/"
                           "sweep.yaml")

    # 4) Launch runs in sequence.
    for run_idx in runs_dict.keys():
        launch_run(run_config=runs_dict[run_idx],
                   sweep_name=str(cur_time),
                   run_index=str(run_idx))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Submit a sweep of synthetically generated jobs.")
    parser.add_argument(
        "--config",
        type=str,
        default="../sweep_examples/cpu_sleep.yaml",
        help="Input YAML config for sweep.",
    )
    parser.add_argument("--debug",
                        action="store_true",
                        help="Enable debug mode")
    args = parser.parse_args()
    sweep_pipeline(sweep_config=args.config)
