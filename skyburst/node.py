class Node(object):
    def __init__(self, num_gpus, num_cpus):
        self.num_gpus = num_gpus
        self.num_cpus = num_cpus
        # Maps gpu index to job occupying that gpu
        self.gpu_dict = {}
        # Maps gpu index to job reserving that gpu
        self.reserved_gpus = {}
        for idx in range(self.num_gpus):
            self.gpu_dict[idx] = None
            self.reserved_gpus[idx] = None
        self.free_gpus = self.num_gpus
        self.free_cpus = self.num_cpus

    def __repr__(self):
        return f'GPU: {self.gpu_dict}, CPU: {self.num_cpus - self.free_cpus}'
