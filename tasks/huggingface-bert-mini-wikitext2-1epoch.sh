#!/bin/bash

# ETA:
# 8 GPU: 5h30m

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
python $SCRIPT_DIR/huggingface-bert-wikitext.py --dataset wikitext-2 --num_train_epochs 1
