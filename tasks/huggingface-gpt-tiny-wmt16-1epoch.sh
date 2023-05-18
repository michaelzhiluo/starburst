#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
python $SCRIPT_DIR/huggingface-gpt-wmt16.py \
    --per_device_train_batch_size 16 \
    --n_embd 256 \
    --n_layer 4 \
    --n_head 4 \
    --num_train_epochs 1
