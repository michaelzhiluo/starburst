import re
import os 
from collections import OrderedDict
import pandas as pd
import yaml
import heapq
import numpy as np
from tabulate import tabulate

def read_yaml(log_path):
	with open(log_path, "r") as f:
		loaded_data = yaml.safe_load(f)
	return loaded_data

def retrieve_events_df(event_number, log_path: str = '../sweep_logs'):
	'''
	Offload all data cleaning to pandas, and none through python
	'''
	
	"""Turns all logs from sweep into a pandas dataframe for analysis"""
	cluster_data_path = f"{log_path}/" + str(event_number) + '/events/'
	job_data_path = f"{log_path}/" + str(event_number) + '/jobs/'
	sweep_data_path = f"{log_path}/" + str(event_number) + "/sweep.yaml"
	
	files = os.listdir(job_data_path)
	for i in range(len(files)):
		file = str(i) + ".yaml"
		cluster_log_path = cluster_data_path + file
		job_log_path = job_data_path + file
		try: 
			cluster_event_data = read_yaml(log_path=cluster_log_path)
			submission_data = read_yaml(log_path=job_log_path)
			with open(sweep_data_path, "r") as f:
				sweep_data = yaml.safe_load(f)
		except Exception as e:
			print(e)
			continue 

	cluster_event_data_df = pd.DataFrame.from_dict(cluster_event_data)
	submission_data_df = pd.DataFrame.from_dict(submission_data)
	sweep_data_df = pd.DataFrame.from_dict(sweep_data)
	return cluster_event_data_df, submission_data_df, sweep_data_df


def gather_job_statistics(cluster_event_df=None, submission_df=None, sweep_df=None, cloud_log_list=None, run_id = 0):
    '''
    Parse all the logs and return a dictionary of jobs.
    '''
    columns = ['idx', 'runtime', 'arrival', 'num_gpus', 'allocated_gpus', 'start', 'num_cpus', 'wait_times', 'state']

    jobs = {}
    for col in columns: 
        jobs[col] = []

    all_nodes = {}
    intervals = {}
    # Process Cloud jobs on Logs
    for job in cloud_log_list:
        match = re.search(r"Job: (\S+) \| Arrival: ([\d.]+) \| Start: +([\d.]+) \| Runtime: (\d+) \| cpu: (\d+) \| gpu: (\d+) \| Preempted: (\S+)", job)
        if match:
            match = match.groups()
            job_name = str(match[0])
            arrival = float(match[1])
            job_id = int(job_name.split('-')[1])
            job_dict = submission_df[job_id]
            arrival = job_dict['scheduler_submit_time']
            submit = float(match[2])
            duration = float(match[3])
            preempted = match[6]
            if preempted == "True":
                continue
            end = submit + 2 + duration             
            times = {"arrival": arrival, "submit": submit, "pod_start": submit + 2, "job_end": end, 'state': 'TIMEOUT-CLOUD', "job_name": job_name}
            intervals[job_id] = times   

    print(f'# Cloud Jobs {len(intervals)}')
    # Process Events DF    
    cluster = cluster_event_df["onprem"]
       
    pod_start_times = {'-'.join(k.split('-')[:3]): v for k,v in cluster['pod_started'].items()}
    job_start_times = cluster['job_successfulcreate']
    all_job_names = list(job_start_times.keys())
    job_end_times = cluster['job_completed']
    # TODO: Verify node names works as intended
    pod_nodes = {'-'.join(k.split('-')[:3]): v for k,v in cluster['pod_node'].items()}
    job_pods = cluster['job_pods']
    # pod_jobs = {value[0]: key for key, value in job_pods.items()}
    nodes_instances = cluster['node_instances']
    temp = 0
    for node in nodes_instances:
        if node not in all_nodes:
            all_nodes[node] = temp
            temp += 1

    for job in all_job_names:
        # if pod in pod_jobs:
        #     job = pod_jobs[pod]
        job_submit = job_start_times[job]
        job_start = pod_start_times[job]

        job_id = int(job.split('-')[1])
        job_arrival = submission_df[job_id]['scheduler_submit_time']
        if job not in job_end_times:
            job_end = job_start + 2 + submission_df[job_id]['job_duration']
        else:
            job_end = job_end_times[job]

        times = {"arrival": job_arrival, \
                # Submit is also job start time
                "submit": job_submit, \
                "pod_start": job_start, \
                "job_end": job_end, \
                "state": "LOCAL", \
                "job_name": job,
            }
        intervals[job_id] = times

    print(f'# Total Jobs {len(intervals)}')

    min_arrival_time = min(v['arrival'] for v in intervals.values())
    # sort intervals by the key
    intervals = OrderedDict(sorted(intervals.items(), key=lambda x: int(x[0])))
    for i, (key, value) in enumerate(intervals.items()):
        job_id = int(key)
        job_name = value['job_name']
        jobs['idx'].append(int(job_id))
        jobs['runtime'].append((value['job_end']-value['pod_start'])/3600.0)
        #real_runtime = value['job_end']-value['pod_start']
        
        jobs['start'].append((value['submit'] - min_arrival_time)/3600.0) # might replace with value['submit']
        jobs['arrival'].append((value['arrival'] - min_arrival_time)/3600.0)
        job_dict = submission_df[job_id]
        #fake_runtime = job_dict['job_duration']
        #print(f'Job {job_id} Real Runtime: {real_runtime} Fake Runtime: {fake_runtime}')
        if job_dict['workload_type'] == 'artifact_eval':
            gpu = int(job_dict['resources']['cpu']//3)
        else:
            gpu = job_dict['resources']['gpu']
        jobs['num_gpus'].append(gpu)
        jobs['num_cpus'].append(submission_df[job_id]['resources']['cpu'])
        jobs['wait_times'].append((value['pod_start']-value['arrival'])/3600.0)
        jobs['state'].append(value['state'])

        if value['state'] == 'TIMEOUT-CLOUD':
            jobs['allocated_gpus'].append({})
        else:
            jobs['allocated_gpus'].append({all_nodes[pod_nodes[job_name]]: []})

    
    hyperparameters = submission_df[run_id]
    jobs['stats'] = hyperparameters
    return jobs 

def index_mapping(jobs=None, gpus_per_node=8, workload='gpu', debug=False):
    '''
    Implement greedly algorithm with heap to place jobs to free resource indicies
    
    Specify which resource (e.g. gpu, cpu) to use fitting jobs to indices
    
    (1) Add all jobs to queue, then greedily assign indicies 
    (2) Have priority queue for each node with "Free indices" sorted by index number 
    (3) Iterate over all start times 

    TODO: Fix 1-off CPU index error 
    TODO: Don't let any job_idx values to be -1, and ensure it starts at node 1
    TODO: Verify allocated_nodes
    TODO: Determine how parsing changes between http_info and default values 
    TODO: Verify arrival value is accurate
    TODO: Create a list of times that include all arrival times and completion times in the same list in numerical order 
    '''
    '''
    if gpu_jobs: 
        gpu_value = 'allocated_gpus_index'
    else: 
        gpu_value = 'allocated_gpus'
    '''
    workload = 'gpu'
    GPUS_PER_NODE = gpus_per_node
    allocated_nodes = set(list(j)[0] for j in jobs['allocated_gpus'] if j)
    nodes = list(range(len(allocated_nodes)))
    
    node_jobs ={}
    node_queues = {}
    for node in nodes:
        node_queues[node] = [i for i in range(GPUS_PER_NODE)]
        node_jobs[node] = []

    global_queue = [] # Queue sorted on end time -- earliest to latest end time
    job_id_to_index = {} 

    for i in range(len(jobs['arrival'])):
        job_id = jobs['idx'][i]
        if jobs['state'][job_id] == 'TIMEOUT-CLOUD':
            continue
        job_node = list(jobs['allocated_gpus'][job_id])[0]
        job_id_to_index[job_id] = i
        if workload == 'gpu':
            job_cpu_size = jobs['num_gpus'][i]
        else: 
            job_cpu_size = jobs['num_cpus'][i]
        job_arrival = jobs['start'][i]
        job_runtime = jobs['runtime'][i]
        
        for end_time, end_job_id in global_queue:
            if job_arrival >= end_time:
                released_index = job_id_to_index[end_job_id]
                for released_node in jobs['allocated_gpus'][released_index]: 
                    released_cpus = jobs['allocated_gpus'][released_index][released_node]
                    released_node_queue = node_queues[released_node]
                    node_jobs[released_node].remove(end_job_id)
                    for cpu in released_cpus:
                        heapq.heappush(released_node_queue, cpu)
                # Remove from global queue
                global_queue.remove((end_time, end_job_id))

        global_queue.append((job_arrival + job_runtime, job_id))
        job_allocated_cpus = []
        node_queue = node_queues[job_node]
        node_jobs[job_node].append(job_id)
        try:
            for j in range(job_cpu_size):
                cpu_index = heapq.heappop(node_queue)
                job_allocated_cpus.append(cpu_index)
        except:
            if debug:
                print("not enough cpus to fit jobs")
                print(node_queue)
                print(job_allocated_cpus)
        
        if debug:
            print(f'job_cpu_size {job_cpu_size}')
            print(f'allocated resources -- cpus or gpus: {job_allocated_cpus}')

        jobs['allocated_gpus'][i] = {job_node: job_allocated_cpus}

    return jobs

def parse_sweep(event_number=0, log_path='../sweep_logs/'):
    #TODO: Move log_jobs from local to remote repo
    events_dfs, submission_df, sweep_df = retrieve_events_df(event_number=event_number)
    runs = {}
    run_id = 0
    cluster_event_df = events_dfs

    estimated_runtimes = []
    for job in submission_df:
        if job == 'hyperparameters':
            continue
        estimated_runtimes.append(submission_df[job]["job_duration"])
    with open(f'{log_path}/{event_number}/events/{0}.log', "r") as f:
        cloud_logs = f.read().split('\n')
    runs = {}
    run  = gather_job_statistics(cluster_event_df=cluster_event_df, submission_df=submission_df, sweep_df=sweep_df, run_id=run_id, cloud_log_list=cloud_logs)
    runs[run_id] = pd.Series(run)
    runs_df = pd.DataFrame.from_dict(runs)
    runs_df = runs_df.transpose()
    return runs_df.loc[0]

def compute_stats(jobs_df, warmup_jobs=5):
    # Computing Simulator stats, such as avg. waiting, avg. JCT, cloud cost, utilization.
    total_waiting_time = 0.0
    total_running_time = 0.0
    num_jobs = 0
    total_cloud_cost = 0
    sum_local_space = 0.0
    sum_cloud_space = 0.0

    start_time = jobs_df['arrival'][warmup_jobs]
    end_time = jobs_df['arrival'][len(jobs_df['arrival']) - warmup_jobs - 1]
    total_jobs = len(jobs_df['arrival'])

    jct_list = []
    wait_list = []

    for idx in range(len(jobs_df['arrival'])):
        job_idx = jobs_df['idx'][idx]
        job_arrival = jobs_df['arrival'][idx]
        job_runtime = jobs_df['runtime'][idx]
        job_start = jobs_df['start'][idx]
        job_state = jobs_df['state'][idx]
        job_gpus = jobs_df['num_gpus'][idx]
        job_cost = jobs_df['num_gpus'][idx] * jobs_df['runtime'][idx]

        inter_start = max(job_start, start_time)
        inter_end = min(job_start + job_runtime, end_time)
        # Cut off beginning and ending of simulator to reach steady state. Calculate the "bleeding".
        if job_idx < warmup_jobs or job_idx > total_jobs - warmup_jobs:
            if job_state == 'LOCAL':
                if inter_end >= inter_start:
                    sum_local_space += job_gpus * (inter_end - inter_start)
            elif job_state == 'TIMEOUT-CLOUD':
                if inter_end >= inter_start:
                    sum_cloud_space += job_gpus * (inter_end - inter_start)
            continue
        # Moved to cloud
        if job_state == 'TIMEOUT-CLOUD':
            total_waiting_time += job_start - job_arrival
            if inter_end >= inter_start:
                sum_cloud_space += job_gpus * (inter_end - inter_start)
            total_cloud_cost += job_cost
        elif job_state == 'LOCAL':
            total_waiting_time += job_start - job_arrival
            if inter_end >= inter_start:
                sum_local_space += job_gpus * (inter_end - inter_start)

        jct_list.append(job_runtime + job_start - job_arrival)
        wait_list.append(job_start - job_arrival)
        total_running_time += job_runtime
        num_jobs += 1

    stats_dict = {}

    stats_dict['total_cloud_cost'] = total_cloud_cost
    stats_dict['avg_cloud_cost'] = total_cloud_cost / (end_time -
                                                                    start_time)
    stats_dict['avg_waiting'] = total_waiting_time / num_jobs
    stats_dict['avg_jct'] = (total_waiting_time +
                                        total_running_time) / num_jobs
    stats_dict['90_jct'] = np.percentile(jct_list,
                                                    90,
                                                    method='nearest')
    stats_dict['99_jct'] = np.percentile(jct_list,
                                                    99,
                                                    method='nearest')

    stats_dict['avg_wait'] = np.mean(wait_list)
    stats_dict['90_wait'] = np.percentile(wait_list,
                                                    90,
                                                    method='nearest')
    stats_dict['99_wait'] = min(
        24, np.percentile(wait_list, 99, method='nearest'))

    stats_dict['cluster_utilization'] = sum_local_space / (
        4 * 8 *
        (end_time - start_time))
    stats_dict['system_utilization'] = (
        sum_local_space + sum_cloud_space) / (4 * 8 * (end_time - start_time))

    headers = ['# Cluster Nodes',
        'Total Cloud Cost', 'Avg. Cloud Cost', 'Avg. Waiting', 'Avg. JCT',
        '90th JCT', '99th JCT', 'Cluster Utilization', 'System Utilization'
    ]
    data = [(4, \
        stats_dict['total_cloud_cost'], stats_dict['avg_cloud_cost'], \
        stats_dict['avg_waiting'], stats_dict['avg_jct'], stats_dict['90_jct'], stats_dict['99_jct'], stats_dict['cluster_utilization'], stats_dict['system_utilization'])]
    print(tabulate(data, headers=headers))
    return stats_dict