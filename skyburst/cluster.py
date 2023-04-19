from skyburst.node import Node
from skyburst import utils


class Cluster(object):
    def __init__(self,
                 num_nodes,
                 num_gpus_per_node=8,
                 binpack='first-fit',
                 backfill=False):
        self.num_nodes = num_nodes
        self.num_gpus_per_node = num_gpus_per_node
        self.nodes = [Node(num_gpus_per_node) for _ in range(num_nodes)]
        self.active_jobs = {}
        self.reserved_jobs = {}
        self.backfill = backfill
        self.binpack = binpack

    def is_full(self):
        return all([n.free_gpus == 0 for n in self.nodes])

    def get_active_jobs(self):
        return self.active_jobs

    def try_fit_v2(self, cur_timestamp, job):
        num_gpus = job.resources['GPUs']

        free_gpus = [n.free_gpus for n in self.nodes]
        node_idx_to_pre_job = {}

        # Quick check, no hope of fitting onto cluster :(
        if num_gpus > sum(free_gpus):
            return False, []

        # Generate job GPU demands
        if num_gpus > self.num_gpus_per_node:
            # Assume worst case colocation
            # Multinode case, i.e. 26 GPUs, 8 GPU/node cluster -> job_gpu_demands = [8,8,8,2]
            job_gpu_demands = [self.num_gpus_per_node] * int(
                num_gpus / self.num_gpus_per_node)
            if num_gpus % self.num_gpus_per_node:
                job_gpu_demands.append(num_gpus % self.num_gpus_per_node)
        else:
            job_gpu_demands = [num_gpus]

        # =============================================================================
        # Generate Job Plans
        # =============================================================================

        # Maps node idx to list of gpu indexes for the job to take
        node_idx_taken = {}
        remove_idx = []

        # Go through free space only first, generate partial plan with free space
        node_free_list = [[] for _ in range(self.num_nodes)]
        node_free_count = [0] * self.num_nodes
        for n_idx, n in enumerate(self.nodes):
            # Go through reserved nodes first
            reserved_list = []
            unreserved_list = []
            for gpu_idx in range(self.num_gpus_per_node):
                if n.reserved_gpus[gpu_idx] and n.gpu_dict[gpu_idx] is None:
                    if n.reserved_gpus[
                            gpu_idx].start >= cur_timestamp + job.runtime:
                        reserved_list.append(gpu_idx)
                elif n.gpu_dict[gpu_idx] is None and n.reserved_gpus[
                        gpu_idx] is None:
                    unreserved_list.append(gpu_idx)
            node_free_list[n_idx] = reserved_list + unreserved_list
            node_free_count[n_idx] = len(node_free_list[n_idx])

        node_free_count = [(n_idx, free_gpu)
                           for n_idx, free_gpu in enumerate(node_free_count)]
        if self.binpack == 'first-fit':
            pass
        elif self.binpack == 'best-fit':
            node_free_count.sort(key=lambda x: x[1])
        elif self.binpack == 'worst-fit':
            node_free_count.sort(key=lambda x: x[1], reverse=True)
        else:
            raise ValueError(f'Invalid allocation strategy {self.binpack}!')

        for list_idx, gpu_demand in enumerate(list(job_gpu_demands)):
            for n_idx, free_gpus in node_free_count:
                if n_idx in node_idx_taken:
                    continue

                if free_gpus >= gpu_demand:
                    # Reserved GPUs in the beginning of list
                    node_idx_taken[n_idx] = node_free_list[n_idx][:gpu_demand]
                    job_gpu_demands.remove(gpu_demand)
                    break

        # If there are still demands that cannot be satisifed via free and preempted jobs,
        # it cannot be scheduled on the cluster.
        if job_gpu_demands:
            return False, []

        # =============================================================================
        # Execute Job Plans
        # =============================================================================
        for n_idx, gpu_demand_list in node_idx_taken.items():
            node = self.nodes[n_idx]
            node.free_gpus -= len(gpu_demand_list)
            if node.free_gpus < 0:
                import pdb
                pdb.set_trace()
                raise ValueError("Should not go here!")
            for idx in gpu_demand_list:
                if node.gpu_dict[idx] is not None:
                    import pdb
                    pdb.set_trace()
                node.gpu_dict[idx] = job
            job.allocated_gpus[n_idx] = gpu_demand_list
        job.start = cur_timestamp
        self.active_jobs[job.idx] = job

        return True, []

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

    def try_clear(self, t: float):
        """Clears cluster of completed jobs at time t.
        """
        completed_jobs = []
        for job_idx, job in self.active_jobs.items():
            # If job has finished before time t...
            if t >= job.start + job.runtime:
                for node_idx, gpu_list in job.allocated_gpus.items():
                    cur_node = self.nodes[node_idx]
                    node_gpu_dict = cur_node.gpu_dict
                    for gpu_idx in gpu_list:
                        node_gpu_dict[gpu_idx] = None
                    cur_node.free_gpus += len(gpu_list)
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
                    if t > 1e6:
                        pass
                    else:
                        raise ValueError('sus')
                for node_idx, gpu_list in r_job.allocated_gpus.items():
                    cur_node = self.nodes[node_idx]
                    for gpu_idx in gpu_list:
                        cur_node.gpu_dict[gpu_idx] = r_job
                        cur_node.reserved_gpus[gpu_idx] = None
                    cur_node.free_gpus -= len(gpu_list)
                    if cur_node.free_gpus < 0:
                        import pdb
                        pdb.set_trace()
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
