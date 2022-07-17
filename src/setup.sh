# Download GPT-2-ja models
wget https://www.nama.ne.jp/models/gpt2ja-small.tar.bz2
wget https://www.nama.ne.jp/models/gpt2ja-medium.tar.bz2

# Unzip
tar xvfj gpt2ja-small.tar.bz2
tar xvfj gpt2ja-medium.tar.bz2

# Optional (not needed)
git clone https://github.com/huggingface/transformers

# Remove bz2 file
rm gpt2ja-small.tar.bz2
rm gpt2ja-medium.tar.bz2
