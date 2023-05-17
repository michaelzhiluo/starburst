from skyburst.node import Node
from skyburst import utils

blocked_by_gpu_cpu_job = 0
blocked_by_cpu_job = 0


class Cluster(object):
    def __init__(self,
                 num_nodes,
                 num_gpus_per_node=8,
                 num_cpus_per_node=96,
                 binpack='first-fit',
                 backfill=False):
        self.num_nodes = num_nodes
        self.num_gpus_per_node = num_gpus_per_node
        self.num_cpus_per_node = num_cpus_per_node
        # List of nodes in the cluster. Assumed homogeneity.
        self.nodes = [
            Node(num_gpus_per_node, num_cpus_per_node)
            for _ in range(num_nodes)
        ]
        # Maps Job ID to Job, active jobs running in the cluster
        self.active_jobs = {}
        # Maps Job ID to Job, reserved jobs to be scheduled in cluster
        self.reserved_jobs = {}
        # This determines whether to binpack with backfill scheduling.
        self.backfill = backfill
        # Defines the bin packing algorithm, `first-fit`, `best-fit`.
        self.binpack = binpack

    def is_full(self):
        return all([n.free_gpus == 0 for n in self.nodes])

    def get_active_jobs(self):
        return self.active_jobs

    def try_fit_v2(self, cur_timestamp, job):
        global blocked_by_cpu_job
        global blocked_by_gpu_cpu_job
        num_gpus = job.resources['GPUs']
        num_cpus = job.resources['CPUs']
        num_cpus_per_node = num_cpus / job.nodes

        free_gpus = [n.free_gpus for n in self.nodes]
        free_cpus = [n.free_cpus for n in self.nodes]
        # Quick check, no hope of fitting onto cluster :(
        if num_gpus > sum(free_gpus) or num_cpus > sum(free_cpus):
            return False, []

        # Generate job GPU demands
        if job.nodes == 1:
            if num_gpus > self.num_gpus_per_node:
                # Assume worst case colocation
                # Multinode case, i.e. 26 GPUs, 8 GPU/node cluster -> job_gpu_demands = [8,8,8,2]
                job_gpu_demands = [self.num_gpus_per_node] * int(
                    num_gpus / self.num_gpus_per_node)
                if num_gpus % self.num_gpus_per_node:
                    job_gpu_demands.append(num_gpus % self.num_gpus_per_node)
            else:
                job_gpu_demands = [num_gpus]
        else:
            job_gpu_demands = [int(num_gpus / job.nodes)] * job.nodes

        # =============================================================================
        # Generate Job Plans
        # =============================================================================
        # Go through free space only first, generate partial plan with free space
        node_free_gpu_list = [
            list(range(self.num_gpus_per_node)) for _ in range(self.num_nodes)
        ]
        node_free_cpu_count = [self.num_cpus_per_node] * self.num_nodes

        # Go through active jobs
        for a_job_idx, a_job in self.active_jobs.items():
            a_job_cpu_per_node = a_job.num_cpus / a_job.nodes
            for n_idx, gpu_list in a_job.allocated_gpus.items():
                for gpu_idx in gpu_list:
                    node_free_gpu_list[n_idx].remove(gpu_idx)
                node_free_cpu_count[n_idx] -= a_job_cpu_per_node

        # Go through reserved jobs
        for r_job_idx, r_job in self.reserved_jobs.items():
            if r_job.start < cur_timestamp + job.runtime:
                r_job_cpu_per_node = r_job.num_cpus / r_job.nodes
                for n_idx, gpu_list in r_job.allocated_gpus.items():
                    for gpu_idx in gpu_list:
                        if not self.nodes[n_idx].gpu_dict[gpu_idx]:
                            node_free_gpu_list[n_idx].remove(gpu_idx)
                node_free_cpu_count[n_idx] -= r_job_cpu_per_node

        node_free_gpu_count = [len(g) for g in node_free_gpu_list]

        node_free_count = [(i, node_free_gpu_count[i], node_free_cpu_count[i])
                           for i in range(len(node_free_gpu_count))]
        if self.binpack == 'first-fit':
            pass
        elif self.binpack == 'best-fit':
            # Sort by nodes with the least free GPU(s).
            node_free_count.sort(key=lambda x: x[1])
        elif self.binpack == 'worst-fit':
            # Sort by nodes with the most free GPU(s). Don't use, very bad.
            node_free_count.sort(key=lambda x: x[1], reverse=True)
        elif self.binpack == 'tetris':
            pass
        else:
            raise ValueError(f'Invalid allocation strategy {self.binpack}!')

        # Maps node idx to list of gpu indexes for the job to take.
        temp = False
        node_idx_taken = {}
        for list_idx, gpu_demand in enumerate(list(job_gpu_demands)):
            for n_idx, free_gpus, free_cpus in node_free_count:
                if n_idx in node_idx_taken:
                    continue
                if free_gpus >= gpu_demand:
                    if free_cpus >= num_cpus_per_node:
                        # TODO: Reserved GPUs in the beginning of list. Prioritize taking reserved.
                        node_idx_taken[n_idx] = node_free_gpu_list[
                            n_idx][:gpu_demand]
                        job_gpu_demands.remove(gpu_demand)
                        break
                    else:
                        pass
                        # if job.num_gpus > 0 and not temp:
                        #     blocked_by_gpu_cpu_job += 1
                        #     temp = True

        # If there are still demands that cannot be satisifed via free and preempted jobs,
        # it cannot be scheduled on the cluster.
        if job_gpu_demands:
            # if temp:
            #     print(
            #         f'GPU-CPU block occurrences: {blocked_by_gpu_cpu_job}, CPU block occurrences: {blocked_by_cpu_job}'
            #     )
            return False, []

        # =============================================================================
        # Execute Job Plans
        # =============================================================================
        # Job plan stores in `node_idx_taken`: {Node Index -> List of GPU Indexes}
        for n_idx, gpu_demand_list in node_idx_taken.items():
            node = self.nodes[n_idx]
            node.free_gpus -= len(gpu_demand_list)
            node.free_cpus -= num_cpus_per_node
            if node.free_gpus < 0 or node.free_cpus < 0:
                raise ValueError('Ran out of cluster resources!')
            for idx in gpu_demand_list:
                if node.gpu_dict[idx] is not None:
                    raise ValueError('Generated execution plan is incorrect.')
                node.gpu_dict[idx] = job
            job.allocated_gpus[n_idx] = gpu_demand_list
        job.start = cur_timestamp
        self.active_jobs[job.idx] = job

        return True, []

    def predict_wait(self, cur_timestamp, job, queue, loop=False):
        max_timestamp = job.deadline - job.runtime

        num_gpus = job.num_gpus

        def get_gpu_demand_list(cur_job):
            num_gpus = job.num_gpus
            if job.nodes == 1:
                if num_gpus > self.num_gpus_per_node:
                    # Assume worst case colocation
                    # Multinode case, i.e. 26 GPUs, 8 GPU/node cluster -> job_gpu_demands = [8,8,8,2]
                    job_gpu_demands = [self.num_gpus_per_node] * int(
                        num_gpus / self.num_gpus_per_node)
                    if num_gpus % self.num_gpus_per_node:
                        job_gpu_demands.append(num_gpus %
                                               self.num_gpus_per_node)
                else:
                    job_gpu_demands = [num_gpus]
            else:
                job_gpu_demands = [int(num_gpus / job.nodes)] * job.nodes
            return job_gpu_demands

        job_gpu_demands = get_gpu_demand_list(job)

        # Generate job GPU demands
        if job.nodes == 1:
            if num_gpus > self.num_gpus_per_node:
                # Assume worst case colocation
                # Multinode case, i.e. 26 GPUs, 8 GPU/node cluster -> job_gpu_demands = [8,8,8,2]
                job_gpu_demands = [self.num_gpus_per_node] * int(
                    num_gpus / self.num_gpus_per_node)
                if num_gpus % self.num_gpus_per_node:
                    job_gpu_demands.append(num_gpus % self.num_gpus_per_node)
            else:
                job_gpu_demands = [num_gpus]
        else:
            job_gpu_demands = [int(num_gpus / job.nodes)] * job.nodes

        node_free_gpu_count = [0] * self.num_nodes

        for n_idx, node in enumerate(self.nodes):
            for gpu_idx in range(self.num_gpus_per_node):
                if node.gpu_dict[gpu_idx]:
                    continue
                node_free_gpu_count[n_idx] += 1

        # "Plan" ahead of the queue
        # for q_job in queue:
        #     q_job_gpu_demands = get_gpu_demand_list(q_job)
        #     q_node_index = can_cluster_fit(node_free_gpu_count)

        active_job_list = [a_job for a_job in self.active_jobs.values()]
        active_job_list.sort(key=lambda x: x.start + x.runtime)

        def can_cluster_fit(free_gpu_count):
            node_indexes = []
            for demand_idx, job_gpu_demand in enumerate(job_gpu_demands):
                for node_idx, free_gpus_node in enumerate(free_gpu_count):
                    if job_gpu_demand <= free_gpus_node \
                        and node_idx not in node_indexes:
                        node_indexes.append(node_idx)
                    if len(node_indexes) == len(job_gpu_demands):
                        return node_indexes
            if len(node_indexes) != len(job_gpu_demands):
                return []
            return node_indexes

        if can_cluster_fit(node_free_gpu_count):
            return True

        for a_job in active_job_list:
            if a_job.start + a_job.runtime > max_timestamp:
                return False
            for n_idx, gpu_list in a_job.allocated_gpus.items():
                node_free_gpu_count[n_idx] += len(gpu_list)

            if can_cluster_fit(node_free_gpu_count):
                return True
        return False

    # Backfill Scheduling: Reserve blocking job.
    def try_reserve(self, cur_timestamp, job):
        max_timestemp = job.deadline - job.runtime

        free_gpus = [n.free_gpus for n in self.nodes]
        active_job_list = [a_job for a_job in self.active_jobs.values()]
        active_job_list.sort(key=lambda x: x.start + x.runtime)

        num_gpus = job.num_gpus
        # Generate job GPU demands
        if num_gpus > self.num_gpus_per_node:
            # Multinode case, i.e. 26 GPUs, 8 GPU/node cluster -> job_gpu_demands = [8,8,8,2]
            job_gpu_demands = [self.num_gpus_per_node] * int(
                num_gpus / self.num_gpus_per_node)
            if num_gpus % self.num_gpus_per_node:
                job_gpu_demands.append(num_gpus % self.num_gpus_per_node)
        else:
            job_gpu_demands = [num_gpus]

        node_free_list = [[] for _ in range(self.num_nodes)]
        node_free_count = [0] * self.num_nodes
        for n_idx, node in enumerate(self.nodes):
            for gpu_idx in range(self.num_gpus_per_node):
                if node.gpu_dict[gpu_idx] or node.reserved_gpus[gpu_idx]:
                    continue
                node_free_count[n_idx] += 1
                node_free_list[n_idx].append(gpu_idx)

        for a_job in active_job_list:
            if a_job.start + a_job.runtime > job.deadline - job.runtime:
                return False
            for n_idx, gpu_list in a_job.allocated_gpus.items():
                for gpu_idx in gpu_list:
                    if self.nodes[n_idx].reserved_gpus[gpu_idx]:
                        continue
                    node_free_list[n_idx].append(gpu_idx)
                    node_free_count[n_idx] += 1

            node_indexes = utils.is_subset(node_free_count, job_gpu_demands)
            if node_indexes:
                for idx, n_idx in enumerate(node_indexes):
                    gpu_list = node_free_list[n_idx][-job_gpu_demands[idx]:]
                    job.allocated_gpus[n_idx] = gpu_list
                    cur_node = self.nodes[n_idx]
                    for gpu_idx in gpu_list:
                        cur_node.reserved_gpus[gpu_idx] = job
                self.reserved_jobs[job.idx] = job
                job.block_job_idx = a_job.idx
                job.start = a_job.start + a_job.runtime
                return True
        raise ValueError('I should not go here!')

    # Backfill Scheduling: Reserve blocking job.
    # def try_reserve(self, cur_timestamp, job):
    #     max_timestemp = job.deadline - job.runtime

    #     active_job_list = [a_job for a_job in self.active_jobs.values()]
    #     active_job_list.sort(key=lambda x: x.start + x.runtime)

    #     num_gpus = job.num_gpus
    #     num_cpus_per_node = job.num_cpus / job.nodes
    #     # Generate job GPU demands
    #     if job.nodes == 1:
    #         if num_gpus > self.num_gpus_per_node:
    #             # Assume worst case colocation
    #             # Multinode case, i.e. 26 GPUs, 8 GPU/node cluster -> job_gpu_demands = [8,8,8,2]
    #             job_gpu_demands = [self.num_gpus_per_node] * int(
    #                 num_gpus / self.num_gpus_per_node)
    #             if num_gpus % self.num_gpus_per_node:
    #                 job_gpu_demands.append(num_gpus % self.num_gpus_per_node)
    #         else:
    #             job_gpu_demands = [num_gpus]
    #     else:
    #         job_gpu_demands = [int(num_gpus / job.nodes)] * job.nodes

    #     node_free_gpu_list = [[] for _ in range(self.num_nodes)]
    #     node_free_gpu_count = [0] * self.num_nodes
    #     node_free_cpus = [0] * self.num_nodes
    #     reserved_cpus = [0] * self.num_nodes
    #     for r_job_idx, r_job in self.reserved_jobs.items():
    #         r_job_cpu_per_node = r_job.num_cpus / r_job.nodes
    #         for n_idx, gpu_list in r_job.allocated_gpus.items():
    #             reserved_cpus[n_idx] += r_job_cpu_per_node

    #     for n_idx, node in enumerate(self.nodes):
    #         for gpu_idx in range(self.num_gpus_per_node):
    #             if node.gpu_dict[gpu_idx] or node.reserved_gpus[gpu_idx]:
    #                 continue
    #             node_free_gpu_count[n_idx] += 1
    #             node_free_gpu_list[n_idx].append(gpu_idx)
    #         node_free_cpus[n_idx] += node.free_cpus

    #     for a_job in active_job_list:
    #         if a_job.start + a_job.runtime > job.deadline - job.runtime:
    #             return False
    #         for n_idx, gpu_list in a_job.allocated_gpus.items():
    #             for gpu_idx in gpu_list:
    #                 if self.nodes[n_idx].reserved_gpus[gpu_idx]:
    #                     continue
    #                 node_free_gpu_list[n_idx].append(gpu_idx)
    #                 node_free_gpu_count[n_idx] += 1
    #             node_free_cpus[n_idx] += a_job.num_cpus / a_job.nodes

    #         node_indexes = []
    #         for demand_idx, job_gpu_demand in enumerate(job_gpu_demands):
    #             for node_idx, free_gpus_node in enumerate(node_free_gpu_count):
    #                 if job_gpu_demand == free_gpus_node \
    #                     and num_cpus_per_node <= node_free_cpus[node_idx] - reserved_cpus[node_idx]\
    #                     and node_idx not in node_indexes:
    #                     node_indexes.append(node_idx)

    #         if len(node_indexes) != len(job_gpu_demands):
    #             continue

    #         if node_indexes:
    #             for idx, n_idx in enumerate(node_indexes):
    #                 gpu_list = node_free_gpu_list[n_idx][
    #                     -job_gpu_demands[idx]:]
    #                 job.allocated_gpus[n_idx] = gpu_list
    #                 cur_node = self.nodes[n_idx]
    #                 for gpu_idx in gpu_list:
    #                     cur_node.reserved_gpus[gpu_idx] = job
    #             self.reserved_jobs[job.idx] = job
    #             job.block_job_idx = a_job.idx
    #             job.start = a_job.start + a_job.runtime
    #             return True
    #     raise ValueError('I should not go here!')

    def try_clear(self, t: float):
        """Clears cluster of completed jobs at time t.
        """
        completed_jobs = []
        # Free jobs on the cluster which have completed.
        for job_idx, job in self.active_jobs.items():
            # If job has finished before time t...
            if t >= job.start + job.runtime:
                for node_idx, gpu_list in job.allocated_gpus.items():
                    cur_node = self.nodes[node_idx]
                    node_gpu_dict = cur_node.gpu_dict
                    for gpu_idx in gpu_list:
                        node_gpu_dict[gpu_idx] = None
                    cur_node.free_gpus += len(gpu_list)
                    cur_node.free_cpus += job.num_cpus / job.nodes
                completed_jobs.append(job)

        # Clears cluster of completed jobs.
        c_job_idx = []
        for job in completed_jobs:
            job.state = 'LOCAL'
            c_job_idx.append(job.idx)
            del self.active_jobs[job.idx]

        # Go through reserved jobs
        r_job_delete_idx = []
        for r_job_idx, r_job in self.reserved_jobs.items():
            # Move reserved job to active jobs
            if r_job.block_job_idx in c_job_idx:
                if t > r_job.start:
                    raise ValueError('sus')
                for node_idx, gpu_list in r_job.allocated_gpus.items():
                    cur_node = self.nodes[node_idx]
                    for gpu_idx in gpu_list:
                        cur_node.gpu_dict[gpu_idx] = r_job
                        cur_node.reserved_gpus[gpu_idx] = None
                    cur_node.free_gpus -= len(gpu_list)
                    cur_node.free_cpus -= r_job.num_cpus / r_job.nodes
                    if cur_node.free_gpus < 0 or cur_node.free_cpus < 0:
                        print(cur_node.free_gpus, cur_node.free_cpus)
                        import pdb
                        pdb.set_trace()
                        raise ValueError('Reserved job, insufficient space.')
                r_job_delete_idx.append(r_job_idx)
                self.active_jobs[r_job_idx] = r_job

        for r_job_idx in r_job_delete_idx:
            del self.reserved_jobs[r_job_idx]

        return completed_jobs

    def __repr__(self):
        repr_str = 'Cluster State:\n'
        for idx, n in enumerate(self.nodes):
            repr_str += f'Node {idx}: {n}\n'
        return repr_str
