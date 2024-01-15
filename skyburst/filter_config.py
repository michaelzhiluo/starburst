def helios_end2end_filter(run_configs):
    temp = []
    for r in run_configs:
        if r['waiting_policy'] == 'zero-1':
            if r['loop'] == 0 and r['max_queue_length'] == 1000000 and r['long_job_thres']==-1 and r['preempt_cloud_ratio'] == -1:
                temp.append(r)
        elif r['waiting_policy'] == 'constant-0.454' and r['preempt_cloud_ratio'] == -1:
            if r['loop'] == 0 and r['max_queue_length'] == 1000000:
                temp.append(r)
        elif r['waiting_policy'] == 'linear_cost_filter_cpu-0.04' and r['long_job_thres']==-1 and r['preempt_cloud_ratio'] == -1:
            if r['loop'] == 1 and r['max_queue_length'] == 10:
                temp.append(r)
        elif r['waiting_policy'] == 'linear_capacity_filter_cpu-0.234':
            if r['loop'] == 1 and r['max_queue_length'] == 10:
                if r['long_job_thres'] > 0 and r['preempt_cloud_ratio'] != -1:
                    temp.append(r)
    return temp

def philly_end2end_filter(run_configs):
    temp = []
    for r in run_configs:
        if r['waiting_policy'] == 'zero-1':
            # No-Wait
            if r['loop'] == 0 and r['max_queue_length'] == 1000000 and r['long_job_thres']==-1 and r['preempt_cloud_ratio'] == -1:
                temp.append(r)
        elif r['waiting_policy'] == 'constant-1' and r['preempt_cloud_ratio'] == -1:
            # Constant Wait and Constant-Wait No-SJ
            if r['loop'] == 0 and r['max_queue_length'] == 1000000:
                temp.append(r)
        elif r['waiting_policy'] == 'linear_cost-0.076' and r['long_job_thres']==-1 and r['preempt_cloud_ratio'] == -1:
            # Starburst (Compute Wait + OO)
            if r['loop'] == 1 and r['max_queue_length'] == 30:
                temp.append(r)
        elif r['waiting_policy'] == 'linear_capacity-0.77':
            # Starburst without Time Estimator (Star Wait + 00)
            if r['loop'] == 1 and r['max_queue_length'] == 30:
                if r['long_job_thres'] > 0 and r['preempt_cloud_ratio'] != -1:
                    temp.append(r)
    return temp

def philly_end2end_pareto(run_configs):
    temp = []
    for r in run_configs:
        asdf = r['waiting_policy'].split('-')[0]
        if asdf == 'constant' and r['loop'] == 0 and r['preempt_cloud_ratio'] == -1:
            # Constant Wait, Constant Wait + No-SJ
            temp.append(r)
        elif asdf == 'linear_cost' and r['loop'] == 1 and r['long_job_thres']==-1 and r['preempt_cloud_ratio'] == -1:
            #  Starburst (Compute Wait + OO)
            temp.append(r)
        elif asdf == 'linear_capacity' and r['loop'] == 1 and r['long_job_thres'] > 0 and r['preempt_cloud_ratio'] != -1:
            # Starburst without Time Estimator (Star Wait + OO)
            temp.append(r)
    return temp

def helios_end2end_pareto(run_configs):
    temp = []
    for r in run_configs:
        asdf = r['waiting_policy'].split('-')[0]
        if asdf == 'constant' and r['loop'] == 0 and r['preempt_cloud_ratio'] == -1:
            # Constant Wait, Constant Wait + No-SJ
            temp.append(r)
        elif asdf == 'linear_cost_filter_cpu' and r['loop'] == 1 and r['long_job_thres']==-1 and r['preempt_cloud_ratio'] == -1:
            #  Starburst (Compute Wait + OO)
            temp.append(r)
        elif asdf == 'linear_capacity_filter_cpu' and r['loop'] == 1 and r['long_job_thres'] > 0 and r['preempt_cloud_ratio'] != -1:
            # Starburst without Time Estimator (Star Wait + OO)
            temp.append(r)
    return temp

def ablate_waiting_policy_fiter(run_configs):
    temp = []
    for r in run_configs:
        if r['waiting_policy'] == 'zero-1' and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1:
            # No-Wait + OO
            temp.append(r)
        elif r['waiting_policy'] == 'constant-0.454' and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1:
            # Constant Wait + OO
            temp.append(r)
        elif r['waiting_policy'] == 'linear_cost-0.04' and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1:
            # Starburst (Compute Wait + OO)
            temp.append(r)
        elif r['waiting_policy'] == 'linear_runtime-0.25' and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1:
            # Runtime Wait + OO
            temp.append(r)
        elif r['waiting_policy'] == 'linear_capacity-0.234':
            # Starburst without Time Estimator (Star Wait + OO)
            if r['long_job_thres'] > 0 and r['preempt_cloud_ratio'] > 0:
                temp.append(r)
            elif r['long_job_thres']==-1 and r['preempt_cloud_ratio'] == -1:
                # Resource-Wait + OO
                temp.append(r)
    return temp

def ablate_waiting_policy_pareto_filter(run_configs):
    temp = []
    for r in run_configs:
        asdf = r['waiting_policy'].split('-')[0]
        if asdf == 'constant' and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1:
            # Constant Wait + OO
            temp.append(r)
        elif asdf == 'linear_cost' and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1:
            # Starburst (Compute Wait + OO)
            temp.append(r)
        elif asdf =='linear_runtime' and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1:
            # Runtime Wait + OO
            temp.append(r)
        elif asdf == 'linear_capacity':
            # Starburst without Time Estimator (Star Wait + OO)
            if r['long_job_thres'] > 0 and r['preempt_cloud_ratio'] > 0:
                temp.append(r)
            elif r['long_job_thres']==-1 and r['preempt_cloud_ratio'] == -1:
                # Resource-Wait + OO
                temp.append(r)
    return temp

def ablate_out_of_order_filter(run_configs):
    temp = []
    for r in run_configs:
        asdf = r['waiting_policy'].split('-')[0]
        if asdf == 'zero' and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1 and r['loop'] ==1:
            # No-Wait
            if 'max_queue_length' in r:
                if r['max_queue_length'] == 1000000:
                    temp.append(r)
            else:
                temp.append(r)
        elif asdf == 'constant' and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1:
            # Constant Wait
            if 'max_queue_length' in r:
                if r['max_queue_length'] == 1000000:
                    temp.append(r)
            else:
                temp.append(r)
        elif (asdf == 'linear_cost_filter_cpu' or asdf == 'linear_cost') and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1:
            # Starburst (Compute Wait)
            if 'max_queue_length' in r:
                if r['max_queue_length'] < 100:
                    temp.append(r)
            else:
                temp.append(r)
        elif (asdf == 'linear_capacity_filter_cpu' or asdf == 'linear_capacity') and r['preempt_cloud_ratio'] > 0 and r['long_job_thres'] > 0:
            # Starburst without Time Estimator (Star Wait)
            if 'max_queue_length' in r:
                if r['max_queue_length'] < 100:
                    temp.append(r)
            else:
                temp.append(r)
    return temp

def ablate_out_of_order_pareto_filter(run_configs):
    temp = []
    for r in run_configs:
        asdf = r['waiting_policy'].split('-')[0]
        if asdf == 'zero' and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1 and r['loop'] ==1:
            # No-Wait
            temp.append(r)
        elif asdf == 'constant' and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1:
            # Constant Wait
            temp.append(r)
        elif asdf == 'linear_cost' and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1:
            # Starburst (Compute Wait)
            temp.append(r)
        elif asdf == 'linear_capacity':
            # Starburst without Time Estimator (Star Wait)
            if r['long_job_thres'] > 0 and r['preempt_cloud_ratio'] > 0:
                temp.append(r)
    return temp

def ablate_jct_percentile(run_configs):
    temp = []
    for r in run_configs:
        asdf = r['waiting_policy'].split('-')[0]
        if asdf == 'constant' and r['loop'] == 0 and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1 and r['max_queue_length'] == 1000000:
            temp.append(r)
        elif asdf == 'linear_cost_filter_cpu' and r['loop'] == 1 and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1 and r['max_queue_length'] == 1000000:
            temp.append(r)
        elif asdf == 'linear_capacity_filter_cpu' and r['loop'] == 1 and r['preempt_cloud_ratio'] > 0 and r['long_job_thres'] > 0 and r['max_queue_length'] == 10:
            temp.append(r)
    return temp

def philly_waiting_budget_pareto_filter(run_configs):
    temp = []
    for r in run_configs:
        asdf = r['waiting_policy'].split('-')[0]
        if asdf == 'constant' and r['loop'] == 1 and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1:
            temp.append(r)
        elif asdf == 'linear_cost' and r['loop'] == 1 and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1:
            temp.append(r)
        elif asdf == 'linear_capacity' and r['loop'] == 1 and r['preempt_cloud_ratio'] > 0 and r['long_job_thres'] > 0:
            temp.append(r)
    return temp

def helios_waiting_budget_pareto_filter(run_configs):
    temp = []
    for r in run_configs:
        asdf = r['waiting_policy'].split('-')[0]
        if asdf == 'constant' and r['loop'] == 1 and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1:
            temp.append(r)
        elif asdf == 'linear_cost_filter_cpu' and r['loop'] == 1 and r['preempt_cloud_ratio'] == -1 and r['long_job_thres']==-1:
            temp.append(r)
        elif asdf == 'linear_capacity_filter_cpu' and r['loop'] == 1 and r['preempt_cloud_ratio'] > 0 and r['long_job_thres'] > 0:
            temp.append(r)
    return temp

def constant_loop_appendix_filter(run_configs):
    temp = []
    for r in run_configs:
        asdf = r['waiting_policy'].split('-')[0]
        if asdf == 'zero' and r['loop'] == 1:
            continue
        temp.append(r)
    return temp

def backfill_appendix_filter(run_configs):
    temp = []
    for r in run_configs:
        if r['waiting_policy'] == 'zero-1':
            if r['loop'] == 0 and r['backfill'] == 0:
                temp.append(r)
        elif r['waiting_policy'] == 'linear_cost-0.076':
            if r['loop'] == 1 and r['backfill'] == 1:
                continue
            temp.append(r)
    run_configs = temp

def philly_data_gravity_filter(run_configs):
    temp = []
    for r in run_configs:
        if r['waiting_policy'] == 'zero-1':
            # No-Wait
            if r['loop'] == 0 and r['max_queue_length'] == 1000000:
                temp.append(r)
        elif r['waiting_policy'] == 'constant-1':
            # Constant Wait and Constant-Wait No-SJ
            if r['loop'] == 0 and r['max_queue_length'] == 1000000:
                temp.append(r)
        elif r['waiting_policy'] == 'linear_cost-0.076':
            # Starburst (Compute Wait + OO)
            if r['loop'] == 1 and r['max_queue_length'] == 30:
                temp.append(r)
    return temp

def ablate_job_offload_filter(run_configs):
    temp = []
    for r in run_configs:
        if r['waiting_policy'] == 'zero-1':
            if r['max_queue_length'] == 1000000:
                temp.append(r)
        elif r['waiting_policy'] == 'linear_cost-0.04':
            if r['max_queue_length'] == 1000000:
                temp.append(r)
        elif r['waiting_policy'] == 'linear_cost_filter_cpu-0.04':
            temp.append(r)
    return temp

# Maps filter names to their config functions.
FILTER_CONFIG_DICT = {
    'helios_end2end': helios_end2end_filter,
    'philly_end2end': philly_end2end_filter,
    'philly_pareto': philly_end2end_pareto,
    'helios_pareto': helios_end2end_pareto,
    'ablate_waiting_policy': ablate_waiting_policy_fiter,
    'ablate_waiting_policy_pareto': ablate_waiting_policy_pareto_filter,
    'ablate_out_of_order': ablate_out_of_order_filter,
    'ablate_out_of_order_pareto': ablate_out_of_order_pareto_filter,
    'ablate_philly_waiting_budget': philly_waiting_budget_pareto_filter,
    'ablate_helios_waiting_budget': helios_waiting_budget_pareto_filter,
    'ablate_jct_percentile': ablate_jct_percentile,
    'philly_end2end_ablate_out_of_order': ablate_out_of_order_filter,
    'appendix_constant_loop': constant_loop_appendix_filter,
    'backfill_appendix': backfill_appendix_filter,
    'philly_data_gravity': philly_data_gravity_filter,
    'ablate_job_offload': ablate_job_offload_filter,
}

# Reduce number of configurations to run (saves time and memory).
def apply_filter_config(name: str, run_configs):
    print('Applying filter config')
    print(f'Num configs: {len(run_configs)}')
    if name not in FILTER_CONFIG_DICT:
        print(f'Filter "{name}" does not exist. Proceeding without a filter')
        return run_configs
    run_configs = FILTER_CONFIG_DICT[name](run_configs)
    print(f'Num configs post filter: {len(run_configs)}')
    return run_configs