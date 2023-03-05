class Job(object):
    def __init__(self, idx: int, arrival: float, runtime: float,
                 deadline: float, resources: dict, cost: float):
        self.idx = idx
        self.arrival = arrival
        self.runtime = runtime
        self.deadline = deadline
        self.resources = resources
        self.num_gpus = resources['GPUs']
        self.cost = cost

        self.state = None
        self.start = None
        self.allocated_gpus = {}

    def __eq__(self, other):
        return self.idx == other.idx

    def __hash__(self):
        return hash(str(self.idx))

    def __repr__(self):
        return f'Job(idx={self.idx}, resources={self.resources}, arr={self.arrival}, run = {self.runtime}, deadline={self.deadline}, start={self.start})\n'
