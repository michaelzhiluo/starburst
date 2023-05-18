#!/bin/bash

# ETA:
# 1 GPU: 40+h
# 2 GPU: 12-13h
# 4 GPU: 9-10h
# 8 GPU: 7-8h

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
python $SCRIPT_DIR/huggingface-gpt-wikitext.py --dataset wikitext-103 --per_device_train_batch_size 4 --num_train_epochs 1
