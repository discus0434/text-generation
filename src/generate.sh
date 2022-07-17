# Generate
python gpt2-japanese/gpt2-generate.py \
    --model checkpoints/gpt2ja-finetune-small \
    --num_generate 100 \
    --temperature 1.0 \
    --min_length 100 \
    --max_length 200
