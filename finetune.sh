# Encode
python gpt2-japanese/encode_bpe.py --src_dir sample_tweet --dst_file finetune

# Fine-Tuning
python gpt2-japanese/run_finetune.py \
    --base_model gpt2ja-small \
    --dataset finetune.npz \
    --run_name gpt2ja-finetune-small

# Generate
python gpt2-japanese/gpt2-generate.py \
    --model gpt2ja-small/gpt2ja-finetune-small \
    --num_generate 10 \
    --top_k 40 \
    --top_p 0.9 \
    --temperature 0.7

# Remove pickle files
for i in `seq 0 7`; do rm tmp$i.pkl; done
