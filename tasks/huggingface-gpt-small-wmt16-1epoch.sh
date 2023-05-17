#!/bin/bash

# ETA:

# 1 GPU: ?
# 2 GPU: ?
# 4 GPU: 5h30m
# 8 GPU: 5h30m

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
python $SCRIPT_DIR/huggingface-gpt-wmt16.py --num_train_epochs 1
