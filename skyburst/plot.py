import math
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.pyplot as plt
import seaborn as sns

GPUS_PER_NODE = 8


def plot_trace_spacetime(jobs, num_nodes):
    jobs = jobs.copy()
    NUM_COLORS = len(jobs['idx'])
    cm = plt.get_cmap('gist_rainbow')
    colors = [cm(1. * i / NUM_COLORS) for i in range(NUM_COLORS)]
    #jobs.sort(key=lambda x: x.idx)
    fig, ax = plt.subplots(figsize=(100, 50))
    total_gpus = num_nodes * GPUS_PER_NODE
    for j_idx in range(len(jobs['idx'])):
        allocated_gpus = jobs['allocated_gpus'][j_idx]
        if not allocated_gpus:
            continue
        else:
            for node_idx in allocated_gpus.keys():
                for node_gpu_idx in allocated_gpus[node_idx]:
                    gpu_idx = total_gpus - (GPUS_PER_NODE * node_idx +
                                            node_gpu_idx)
                    #                 print(job.idx)
                    #                 print(len(colors))
                    ax.barh(gpu_idx,
                            width=jobs['runtime'][j_idx],
                            edgecolor='black',
                            height=1.0,
                            left=jobs['start'][j_idx],
                            align='edge',
                            color=colors[jobs['idx'][j_idx]])
    import math
    for i in range(total_gpus + 1):
        multiplier = math.ceil(num_nodes / 32)
        if (i + 1) % GPUS_PER_NODE == 1:
            plt.axhline(y=i + 1, linewidth=8 / multiplier, color='brown')
        else:
            plt.axhline(y=i + 1,
                        linewidth=1 / multiplier,
                        color='black',
                        linestyle='--')
    max_arrival = max(jobs['arrival'])
    plt.ylim(bottom=1, top=total_gpus + 1)
    plt.xlim(right=1.5 * max_arrival)
    plt.axvline(x=max_arrival, color='black', linewidth=5)
    plt.tight_layout()
    plt.show()


def plot_trace_spacetime_and_spillover(jobs, num_nodes):
    jobs = jobs.copy()
    NUM_COLORS = len(jobs['idx']) + 5
    cm = plt.get_cmap('gist_rainbow')
    colors = [cm(1. * i / NUM_COLORS) for i in range(NUM_COLORS)]
    fig, ax = plt.subplots(figsize=(100, 50))
    total_gpus = num_nodes * GPUS_PER_NODE
    segment_height_list = {}
    for j_idx in range(len(jobs['idx'])):
        allocated_gpus = jobs['allocated_gpus'][j_idx]
        if not allocated_gpus:
            height = 1
            segment = (jobs['arrival'][j_idx],
                       jobs['arrival'][j_idx] + jobs['runtime'][j_idx], j_idx)
            for k, v in segment_height_list.items():
                if segment[0] > k[0] and segment[0] < k[1]:
                    height += v
            segment_height_list[segment] = jobs['num_gpus'][j_idx]
            ax.barh(total_gpus + height,
                    width=segment[1] - segment[0],
                    edgecolor='black',
                    height=jobs['num_gpus'][j_idx],
                    left=segment[0],
                    align='edge',
                    alpha=0.5,
                    color=colors[jobs['idx'][j_idx]])
        else:
            for node_idx in allocated_gpus.keys():
                for node_gpu_idx in allocated_gpus[node_idx]:
                    gpu_idx = total_gpus - (GPUS_PER_NODE * node_idx +
                                            node_gpu_idx)
                    #                 print(job.idx)
                    #                 print(len(colors))
                    ax.barh(gpu_idx,
                            width=jobs['runtime'][j_idx],
                            edgecolor='black',
                            height=1.0,
                            alpha=0.5,
                            left=jobs['start'][j_idx],
                            align='edge',
                            color=colors[jobs['idx'][j_idx]])
    for i in range(total_gpus + 1):
        multiplier = math.ceil(num_nodes / 32)
        if (i + 1) % GPUS_PER_NODE == 1:
            plt.axhline(y=i + 1, linewidth=8 / multiplier, color='brown')
        else:
            pass
    max_arrival = max(jobs['arrival'])
    plt.ylim(bottom=1)  #, #top=total_gpus + 1)
    plt.xlim(right=1.4 * max_arrival)
    plt.axvline(x=max_arrival, color='black', linewidth=5)
    plt.tight_layout()
    plt.show()


def visualize_jobs(jobs, mode='all'):
    jobs = jobs.copy()
    NUM_COLORS = len(jobs)
    cm = plt.get_cmap('gist_rainbow')
    colors = [cm(1. * i / NUM_COLORS) for i in range(NUM_COLORS)]
    jobs.sort(key=lambda x: x.idx)
    x = [(j.arrival, j.deadline) for j in jobs]
    fig, ax = plt.subplots(figsize=(100, 50))

    count = 0
    for i, evt in enumerate(x):
        if mode == 'all':
            mask = 1
        elif mode == 'cloud':
            if jobs[i].start is None:
                mask = 1
            else:
                mask = 0
        elif mode == 'local':
            if jobs[i].start is None:
                mask = 0
            else:
                mask = 1


#         ax.barh(count,
#                 width=(evt[1]-evt[0]),
#                 edgecolor='black' if mask else None,
#                 height=1.0*jobs[i].num_gpus,
#                 left=evt[0],
#                 align='edge',
#                 color=colors[i] if mask else 'grey')
        ax.barh(count,
                width=mask * (evt[1] - evt[0]),
                edgecolor='black' if mask else None,
                height=1.0 * jobs[i].num_gpus,
                left=evt[0],
                align='edge',
                color=colors[i] if mask else None)

        count += jobs[i].num_gpus
    ax.get_yaxis().set_visible(False)
    plt.xlabel('Time Quantums')
    plt.show()
