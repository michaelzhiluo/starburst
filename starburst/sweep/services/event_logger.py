import copy
from enum import Enum
import os
import time
import traceback
from typing import Any, Dict

from kubernetes import client, config

from starburst.sweep import utils, submit_sweep
from starburst.utils import LogManager

EVENT_DATA_TEMPLATE = {
    'job_pods': {},
    'node_instances': {},
    'pod_logs': {},
    'pod_node': {}
}
EVENT_LOG_FREQUENCY = 0.5


class PodStatus(Enum):
    """
    Kubernetes pod status states.
    """
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


def check_if_pod_logs_exist(status: str):
    """
    Checks if the pod logs exist for the given status.
    """
    return status in [
        PodStatus.RUNNING.value, PodStatus.SUCCEEDED.value,
        PodStatus.FAILED.value
    ]


def get_event_logger_log_path(name: str):
    """
    Retrieves the path to the job submission log file.
    """
    path = (f"{submit_sweep.LOG_DIRECTORY.format(name=name)}"
            "/debug/event_logger.log")
    return os.path.abspath(path)


def get_pod_events_path(name: str, idx: int):
    """
    Retrives the path to YAML file that stores pod/job events.
    """
    log_path = submit_sweep.LOG_DIRECTORY.format(name=name) + '/events/'
    return f"{log_path}{idx}.yaml"


def retrieve_node_instance(api: client.CoreV1Api) -> Dict[str, str]:
    """
    Retrieves the instance type for each node in the cluster.
    """
    node_list = api.list_node().items
    instance_types = {}
    for node_data in node_list:
        node_name = node_data.metadata.name
        for label, value in node_data.metadata.labels.items():
            if label == "node.kubernetes.io/instance-type":
                instance_types[node_name] = value
                break
    return instance_types


def event_logger_loop(clusters: Dict[str, Any], jobs: Dict[Any, Any],
                      sweep_name: str, run_index: int,
                      file_logger: LogManager):
    """
    Loop for logging events from the cluster.

    Args:
        clusters (Dict[str, Any]): Dictionary of cluster types and their names.
        jobs (Dict[Any, Any]): Dictionary of job ids and their job data.
        sweep_name (str): Name of the sweep.
        run_index (int): Index of the run.
        file_logger (LogFileManager): File logger for logging
                                                   events.
    """

    cluster_event_data = {}
    events_log_path = get_pod_events_path(sweep_name, run_index)
    apis = {}

    # Preprocessing cluster event data.
    for cluster_cls, cluster_config in clusters.items():
        cluster_name = cluster_config['cluster_name']
        cluster_type = cluster_config['cluster_type']
        if cluster_type != 'k8':
            continue
        config.load_kube_config(context=cluster_name)
        apis[cluster_cls] = client.CoreV1Api()
        cluster_event_data[cluster_cls] = copy.deepcopy(EVENT_DATA_TEMPLATE)
        event_data = cluster_event_data[cluster_cls]
        event_data['node_instances'] = retrieve_node_instance(
            apis[cluster_cls])

    total_jobs = len(jobs)
    scheduled_pods = set()
    finished_jobs = set()
    while True:
        for cluster_cls, cluster_config in clusters.items():
            if cluster_cls not in apis:
                continue
            cluster_name = cluster_config['cluster_name']
            config.load_kube_config(context=cluster_name)
            api = apis[cluster_cls]
            # Get all events
            events = api.list_event_for_all_namespaces()
            # Get all pods
            pod_list = api.list_namespaced_pod(namespace="default")

            event_data = cluster_event_data[cluster_cls]
            for pod in pod_list.items:
                pod_name = pod.metadata.name
                if 'job' not in pod_name:
                    continue
                pod_status = pod.status.phase
                if pod_name not in scheduled_pods:
                    event_data['pod_node'][pod_name] = pod.spec.node_name
                    scheduled_pods.add(pod_name)

                if check_if_pod_logs_exist(pod_status):
                    pod_logs = api.read_namespaced_pod_log(name=pod_name,
                                                           namespace="default",
                                                           previous=False)
                    event_data['pod_logs'][pod_name] = pod_logs

            # Parsing Events
            for item in events.items:
                involved_object = item.involved_object
                event_reason = item.reason
                name = involved_object.name
                # Filter out pods that are not related to the sweep of jobs.
                if 'job' not in name or name in finished_jobs:
                    continue
                event_key = None
                if involved_object.kind == 'Pod':
                    file_logger.append(f'Pod {name} - {event_reason}')
                    event_key = f'pod_{event_reason}'
                    event_value = int(item.first_timestamp.timestamp())
                elif involved_object.kind == 'Job':
                    file_logger.append(f'Job {name} - {event_reason}')
                    event_key = f'Job_{event_reason}'
                    event_value = int(item.first_timestamp.timestamp())
                    # Special handling when job completes.
                    if event_reason == 'Completed':
                        pods = api.list_namespaced_pod(
                            namespace='default',
                            label_selector=f"job-name={name}").items
                        event_data['job_pods'][name] = [
                            pod.metadata.name for pod in pods
                        ]
                        finished_jobs.add(name)
                if event_key is not None:
                    event_key = event_key.lower()
                    if event_key not in event_data:
                        event_data[event_key] = {}
                    event_data[event_key][name] = event_value

            v1 = client.CoreV1Api()
            batch_v1 = client.BatchV1Api()
            jobs = batch_v1.list_namespaced_job('default')
            for job in jobs.items:
                pod_selector = job.spec.selector.match_labels
                # Get pods of the job
                pod_selector_string = ",".join(
                    [f"{k}={v}" for k, v in pod_selector.items()])
                pods = v1.list_namespaced_pod(
                    'default', label_selector=pod_selector_string)

                # List of nodes to which the job's pods have been assigned
                # nodes = [
                #     pod.spec.node_name for pod in pods.items
                #     if pod.spec.node_name is not None
                # ]
                nodes = [pod.status.conditions for pod in pods.items]
                file_logger.append(str(nodes))

        utils.save_yaml_object(cluster_event_data, events_log_path)
        time.sleep(EVENT_LOG_FREQUENCY)
        file_logger.append(f"==========Event Logging Loop; Run: {run_index}, "
                           f"Time {time.time()}==========")

        if len(finished_jobs) == total_jobs:
            file_logger.append(f"Finished logging for Run: {run_index}")
            break


def logger_service(clusters: Dict[str, str], jobs: Dict[Any, Any],
                   sweep_name: str, run_index: int):
    """
    Service that logs events and pod logs for the sweep.
    """
    event_loop_logger = LogManager("event_logger_service",
                                   get_event_logger_log_path(sweep_name))
    try:
        event_logger_loop(clusters=clusters,
                          jobs=jobs,
                          sweep_name=sweep_name,
                          run_index=run_index,
                          file_logger=event_loop_logger)
    except Exception:
        # If an error occrus during job submission loop, log the error
        # and move onto the next run in the sweep.
        exception_str = traceback.format_exc() + "\n"
        event_loop_logger.append(exception_str)
        pass
    event_loop_logger.close()
