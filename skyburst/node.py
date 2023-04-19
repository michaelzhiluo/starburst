class Node(object):
    def __init__(self, num_gpus):
        self.num_gpus = num_gpus
        self.gpu_dict = {}
        self.reserved_gpus = {}
        for idx in range(self.num_gpus):
            self.gpu_dict[idx] = None
            self.reserved_gpus[idx] = None
        self.free_gpus = num_gpus

    def __repr__(self):
        return f'{self.gpu_dict}'
