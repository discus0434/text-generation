# Generate
mkdir dist -p
python gpt2-japanese/gpt2-generate.py \
    --model checkpoints/gpt2ja-finetune-small \
    --num_generate 10 \
    --temperature 1.0 \
    --min_length 150 \
    --max_length 250 \
    --output_file dist/dist.txt
