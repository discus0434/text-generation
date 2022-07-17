# Generate
python gpt2-japanese/gpt2-generate.py \
    --model gpt2ja-small/gpt2ja-finetune-small \
    --num_generate 10 \
    --top_k 40 \
    --top_p 0.9 \
    --temperature 0.7
