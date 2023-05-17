#!/bin/bash

# ETA:
# 1 GPU: ?
# 2 GPU: ?
# 4 GPU: ?
# 8 GPU: ?

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
python $SCRIPT_DIR/huggingface-bert-wikitext.py --num_train_epochs 1
