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

        # State of the Job
        self.state = None
        # Starting time of the job on the local cluster, if none, the job was ran on the cloud.
        self.start = None

        # Keeps track of which GPU(s) the job ran on.
        self.allocated_gpus = {}

        # This for preemption, to prevent chain pre-emptions
        self.opp_cost = 0

    def __eq__(self, other):
        return self.idx == other.idx

    def __hash__(self):
        return hash(str(self.idx))

    def __repr__(self):
        return f'Job(idx={self.idx}, resources={self.resources}, arr={self.arrival}, run = {self.runtime}, deadline={self.deadline}, start={self.start})\n'
