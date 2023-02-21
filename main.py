import argparse
import csv
import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
import os

from skyburst.traces import philly

LOGDIR = '../philly-traces/trace-data'

parser = argparse.ArgumentParser(
    prog='SkyBurst: Hybrid cloud simulator for Sky',
    description='Runs a cloud simulation for SkyBurst')

cluster_job_log_path = os.path.join(LOGDIR, 'cluster_job_log')
with open(cluster_job_log_path, 'r') as f:
    cluster_job_log = json.load(f)
jobs = [
    philly.JobTrace(status=job['status'],
                    jobid=job['jobid'],
                    attempts=job['attempts'],
                    submitted_time=job['submitted_time'],
                    user=job['user']) for job in cluster_job_log
]
