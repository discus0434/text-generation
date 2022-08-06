#!/bin/bash

# Generate
mkdir dist -p
python gpt2-japanese/gpt2-generate.py \
    --model checkpoints/gpt2ja-2022-07-26-finetune-small \
    --num_generate 1000 \
    --temperature 1.0 \
    --min_length 120 \
    --max_length 139 \
    --output_file dist/out.txt
