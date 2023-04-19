from typing import Any, List


def generate_sorting_function(sched_alg: str):
    if sched_alg == 'fifo':
        sort_func = lambda x: x.arrival
    elif sched_alg == 'lifo':
        sort_func = lambda x: -x.arrival
    elif sched_alg == 'edf':
        sort_func = lambda x: x.deadline
    elif sched_alg == 'evdf':
        sort_func = lambda x: x.deadline * x.num_gpus
    elif sched_alg == 'ldf':
        sort_func = lambda x: -x.deadline
    elif sched_alg == 'sjf':
        sort_func = lambda x: x.runtime
    elif sched_alg == 'svjf':
        sort_func = lambda x: x.cost
    elif sched_alg == 'ljf':
        sort_func = lambda x: -x.runtime
    elif sched_alg == 'lvjf':
        sort_func = lambda x: -x.cost
    elif sched_alg == 'swf':
        sort_func = lambda x: x.deadline - x.runtime
    elif sched_alg == 'svwf':
        sort_func = lambda x: (x.deadline - x.runtime) * x.num_gpus
    elif sched_alg == 'lwf':
        sort_func = lambda x: -x.deadline + x.runtime
    else:
        raise ValueError(
            f'Scheudling algorithm {sched_alg} does not match existing policies.'
        )
    return sort_func


def is_subset(list1: List[Any], list2: List[Any]):
    """Checks if list1 is a subset of list2 and returns the matching indexes of the subset."""
    indexes = []
    for i2, elem in enumerate(list2):
        for i1, x in enumerate(list1):
            if x == elem and i1 not in indexes:
                indexes.append(i1)
                break
        if len(indexes) != i2 + 1:
            return []
    return indexes
