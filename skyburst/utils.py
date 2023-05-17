import itertools
import pickle
from typing import Any, List

import pandas as pd


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


def convert_to_lists(d: dict):
    for key, value in d.items():
        # If the value is a dictionary, recursively convert it to a list
        if isinstance(value, dict):
            d[key] = convert_to_lists(value)
        elif not isinstance(value, list):
            d[key] = [value]
    return d


def flatten_dict(nested_dict, parent_key='', sep=':', preserve_name=False):
    flattened_dict = {}
    for key, value in nested_dict.items():
        if preserve_name:
            new_key = key
        else:
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            flattened_dict.update(
                flatten_dict(value,
                             new_key,
                             sep=sep,
                             preserve_name=preserve_name))
        else:
            flattened_dict[new_key] = value
    return flattened_dict


def unflatten_dict(flattened_dict, sep=':'):
    unflattened_dict = {}
    for key, value in flattened_dict.items():
        parts = key.split(sep)
        current_dict = unflattened_dict
        for part in parts[:-1]:
            current_dict = current_dict.setdefault(part, {})
        current_dict[parts[-1]] = value
    return unflattened_dict


def generate_cartesian_product(d: dict):
    d = flatten_dict(d)
    print(d)
    # Get the keys and values from the outer dictionary
    keys = list(d.keys())
    values = list(d.values())

    # Use itertools.product to generate the cartesian product of the values
    product = itertools.product(*values)

    # Create a list of dictionaries with the key-value pairs for each combination
    result = [dict(zip(keys, p)) for p in product]
    # Return the list of dictionaries
    return [unflatten_dict(r) for r in result]


def is_subset(list1: List[Any], list2: List[Any]):
    """Checks if list2 is a subset of list1 and returns the matching indexes of the subset."""
    indexes = []
    for i2, elem in enumerate(list2):
        for i1, x in enumerate(list1):
            if x == elem and i1 not in indexes:
                indexes.append(i1)
                break
        if len(indexes) != i2 + 1:
            return []
    return indexes


def _load_logs(file_path: str):
    file = open(file_path, 'rb')
    return pickle.load(file)


def load_logs_as_dataframe(file_path: str):
    simulator_results = _load_logs(file_path)
    for r in simulator_results:
        if 'snapshot' in r:
            r['snapshot'] = [r['snapshot']]
    simulator_results = [
        flatten_dict(r, preserve_name=True) for r in simulator_results
    ]
    return pd.DataFrame(simulator_results)
