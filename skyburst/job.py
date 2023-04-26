class Job(object):
    def __init__(self,
                 idx: int,
                 arrival: float = 0.0,
                 runtime: float = 0.0,
                 deadline: float = 0.0,
                 resources: dict = None,
                 cost: float = 0.0,
                 nodes: int = 1):
        self.idx = idx
        self.arrival = arrival
        self.runtime = runtime
        self.deadline = deadline
        self.resources = resources
        if 'GPUs' in resources:
            self.num_gpus = resources['GPUs']
        else:
            self.resources['GPUs'] = 0
            self.num_gpus = 0

        if 'CPUs' in resources:
            self.num_cpus = resources['CPUs']
        else:
            self.resources['CPUs'] = 0
            self.num_cpus = 0

        self.cost = cost
        self.nodes = nodes

        # State of the Job
        self.state = None
        # Starting time of the job on the local cluster, if none, the job was ran on the cloud.
        self.start = None

        # Keeps track of which GPU(s) the job ran on.
        self.allocated_gpus = {}

        # For backfill scheduling, job immediately executed after Job idx `block_job_idx` completes.
        self.block_job_idx = None

        # This field keeps track of the total starved space a job has incurred due to preemption.
        # This is to prevent chain preemptions.
        self.starved_space = 0

    def __eq__(self, other):
        return self.idx == other.idx

    def __hash__(self):
        return hash(str(self.idx))

    def set_deadline(self, deadline):
        self.deadline = deadline

    def __repr__(self):
        return f'Job(idx={self.idx}, resources={self.resources}, arr={self.arrival}, run = {self.runtime}, deadline={self.deadline}, start={self.start})\n'
