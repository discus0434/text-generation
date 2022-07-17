
# japanese-pretrained-models 

## (previously: japanese-gpt2)

![rinna-icon](./rinna.png)

This repository provides the code for training Japanese pretrained models. This code has been used for producing [japanese-gpt2-medium](https://huggingface.co/rinna/japanese-gpt2-medium), [japanese-gpt2-small](https://huggingface.co/rinna/japanese-gpt2-small), [japanese-gpt2-xsmall](https://huggingface.co/rinna/japanese-gpt2-xsmall), and [japanese-roberta-base](https://huggingface.co/rinna/japanese-roberta-base) released on HuggingFace model hub by [rinna Co., Ltd.](https://corp.rinna.co.jp/)

Currently supported pretrained models include: [GPT-2](https://d4mucfpksywv.cloudfront.net/better-language-models/language-models.pdf), [RoBERTa](https://arxiv.org/pdf/1907.11692.pdf).

| Table of Contents |
|-|
| [Update log](#update-log) |
| [Use tips](#use-tips) |
| [Use our pretrained models via Huggingface](#use-our-pretrained-models-via-huggingface) |
| [Train `japanese-gpt2-xsmall` from scratch](#train-japanese-gpt2-xsmall-from-scratch) |
| [Train `japanese-roberta-base` from scratch](#train-japanese-roberta-base-from-scratch) |
| [License](#license) |

---

**Please open an issue (in English/日本語) if you encounter any problem using the code or using our models via Huggingface.**

if you find this work useful, please cite the following paper:

~~~
@article{rinna_pretrained2021,
    title={日本語自然言語処理における事前学習モデルの公開},
    author={趙 天雨 and 沢田 慶},
    journal={人工知能学会研究会資料 言語・音声理解と対話処理研究会},
    volume={93},
    pages={169-170},
    year={2021},
    doi={10.11517/jsaislud.93.0_169}
}
~~~

---

## Update log

* 2022/01/25 Updated link to `rinna/japanese-gpt-1b` in the model summary table.
 
* 2022/01/17 Updated citation information.

* 2021/11/01 Updated corpora links.

* 2021/09/13 Added tips on using `position_ids` with `japanese-roberta-base`. Refer to [issue 3](https://github.com/rinnakk/japanese-pretrained-models/issues/3) for details.

* 2021/08/26 **\[Important\]** Updated license from the MIT license to the Apache 2.0 license due to the use of the Wikipedia pre-processing code from [cl-tohoku/bert-japanese](https://github.com/cl-tohoku/bert-japanese). See [issue 1](https://github.com/rinnakk/japanese-pretrained-models/issues/1) for details.

* 2021/08/23 Added Japanese Wikipedia to training corpora. Published code for training `rinna/japanese-gpt2-small`, `rinna/japanese-gpt2-xsmall`, and `rinna/japanese-roberta-base`.

* 2021/08/18 Changed repo name from `japanese-gpt2` to `japanese-pretrained-models`

* 2021/06/15 Fixed best PPL tracking bug when using a checkpoint.

* 2021/05/04 Fixed random seeding bug for Multi-GPU training.

* 2021/04/06 Published code for training `rinna/japanese-gpt2-medium`.

---

## Use tips

### Tips for `rinna/japanese-roberta-base`

* Use `[CLS]`: To predict a masked token, be sure to add a `[CLS]` token before the sentence for the model to correctly encode it, as it is used during the model training.

* Use `[MASK]` after tokenization: A) Directly typing `[MASK]` in an input string and B) replacing a token with `[MASK]` after tokenization will yield different token sequences, and thus different prediction results. It is more appropriate to use `[MASK]` after tokenization (as it is consistent with how the model was pretrained). However, the Huggingface Inference API only supports typing `[MASK]` in the input string and produces less robust predictions.

* Provide `position_ids` as an argument explicitly: When `position_ids` are not provided for a `Roberta*` model, Huggingface's `transformers` will automatically construct it but start from `padding_idx` instead of `0` (see [issue](https://github.com/rinnakk/japanese-pretrained-models/issues/3) and function `create_position_ids_from_input_ids()` in Huggingface's [implementation](https://github.com/huggingface/transformers/blob/master/src/transformers/models/roberta/modeling_roberta.py)), which unfortunately does not work as expected with `rinna/japanese-roberta-base` since the `padding_idx` of the corresponding tokenizer is not `0`. So please be sure to constrcut the `position_ids` by yourself and make it start from position id `0`.

---

## Use our pretrained models via Huggingface

### Model summary

| language model | # params | # layers | # emb dim | # epochs | dev ppl | training time\* |
|-|-|-|-|-|-|-|
| [rinna/japanese-gpt-1b](https://huggingface.co/rinna/japanese-gpt-1b) | 1.3B | 24 | 2048 | 10+ | 13.9 | n/a\*\* |
| [rinna/japanese-gpt2-medium](https://huggingface.co/rinna/japanese-gpt2-medium) | 336M | 24 | 1024 | 4 | 18 | 45 days |
| [rinna/japanese-gpt2-small](https://huggingface.co/rinna/japanese-gpt2-small) | 110M | 12 | 768 | 3 | 21 | 15 days |
| [rinna/japanese-gpt2-xsmall](https://huggingface.co/rinna/japanese-gpt2-xsmall) | 37M | 6 | 512 | 3 | 28 | 4 days |

| masked language model | # params | # layers | # emb dim | # epochs | dev ppl | training time\* |
|-|-|-|-|-|-|-|
| [rinna/japanese-roberta-base](https://huggingface.co/rinna/japanese-roberta-base) | 110M | 12 | 768 | 8 | 3.9 | 15 days |

*\* Training was conducted on a 8x V100 32GB machine.*

*\*\* Training was conducted using a different codebase and a different computing environment.*

### Example: use `rinna/japanese-roberta-base` for predicting masked token

~~~
import torch
from transformers import T5Tokenizer, RobertaForMaskedLM

# load tokenizer
tokenizer = T5Tokenizer.from_pretrained("rinna/japanese-roberta-base")
tokenizer.do_lower_case = True  # due to some bug of tokenizer config loading

# load model
model = RobertaForMaskedLM.from_pretrained("rinna/japanese-roberta-base")
model = model.eval()

# original text
text = "4年に1度オリンピックは開かれる。"

# prepend [CLS]
text = "[CLS]" + text

# tokenize
tokens = tokenizer.tokenize(text)
print(tokens)  # output: ['[CLS]', '▁4', '年に', '1', '度', 'オリンピック', 'は', '開かれる', '。']']

# mask a token
masked_idx = 5
tokens[masked_idx] = tokenizer.mask_token
print(tokens)  # output: ['[CLS]', '▁4', '年に', '1', '度', '[MASK]', 'は', '開かれる', '。']

# convert to ids
token_ids = tokenizer.convert_tokens_to_ids(tokens)
print(token_ids)  # output: [4, 1602, 44, 24, 368, 6, 11, 21583, 8]

# convert to tensor
token_tensor = torch.LongTensor([token_ids])

# provide position ids explicitly
position_ids = list(range(0, token_tensor.size(1)))
print(position_ids)  # output: [0, 1, 2, 3, 4, 5, 6, 7, 8]
position_id_tensor = torch.LongTensor([position_ids])

# get the top 10 predictions of the masked token
with torch.no_grad():
    outputs = model(input_ids=token_tensor, position_ids=position_id_tensor)
    predictions = outputs[0][0, masked_idx].topk(10)

for i, index_t in enumerate(predictions.indices):
    index = index_t.item()
    token = tokenizer.convert_ids_to_tokens([index])[0]
    print(i, token)

"""
0 総会
1 サミット
2 ワールドカップ
3 フェスティバル
4 大会
5 オリンピック
6 全国大会
7 党大会
8 イベント
9 世界選手権
"""
~~~

---

## Train `japanese-gpt2-xsmall` from scratch

### Install dependencies

Install required packages by running the following command under the repo directory:

~~~
pip install -r requirements.txt
~~~

### Data construction and model training

1. Set up [fugashi](https://github.com/polm/fugashi) tokenzier for preprocessing Wikipedia corpus by running:
~~~
python -m unidic download
~~~

2. Download training corpus [Japanese CC-100](http://data.statmt.org/cc-100/) and extract the `ja.txt` file.

3. Move the `ja.txt` file or modify `src/corpus/jp_cc100/config.py` to match the filepath of `ja.txt` with `self.raw_data_dir` in the config file.

4. Split `ja.txt` to smaller files by running:
~~~~
cd src/
python -m corpus.jp_cc100.split_to_small_files
~~~~

5. First check the versions of Wikipedia dump at [Wikipedia cirrussearch](https://dumps.wikimedia.org/other/cirrussearch/) and fill in `self.download_link` (in file `src/corpus/jp_wiki/config.py`) with the link to your preferred Wikipedia dump version. Then download training corpus Japanese Wikipedia and split it by running:
~~~
python -m corpus.jp_wiki.build_pretrain_dataset
python -m corpus.jp_wiki.split_to_small_files
~~~

6. Train a xsmall-sized GPT-2 on, for example, 4 V100 GPUs by running:
~~~~
CUDA_VISIBLE_DEVICES=0,1,2,3 python -m task.pretrain_gpt2.train \
    --n_gpus 4 \
    --save_model True \
    --enable_log True \
    --model_size xsmall \
    --model_config_filepath model/gpt2-ja-xsmall-config.json \
    --batch_size 20 \
    --eval_batch_size 40 \
    --n_training_steps 1600000 \
    --n_accum_steps 3 \
    --init_lr 0.0007
~~~~

### Interact with the trained model

Assume you have run the training script and saved your xsmall-sized GPT-2 to `data/model/pretrain_gpt2/gpt2-ja-xsmall-xxx.checkpoint`. Run the following command to use it to complete text on one GPU by nucleus sampling with `p=0.95` and `k=40`:

~~~~
CUDA_VISIBLE_DEVICES=0 python -m task.pretrain_gpt2.interact \
    --checkpoint_path ../data/model/pretrain_gpt2/gpt2-ja-medium-xxx.checkpoint \
    --gen_type top \
    --top_p 0.95 \
    --top_k 40
~~~~

### Prepare files for uploading to Huggingface

1. Make your Huggingface account. Create a model repo. Clone it to your local machine.

2. Create model and config files from a checkpoint by running:
~~~~
python -m task.pretrain_gpt2.checkpoint2huggingface \
    --checkpoint_path ../data/model/gpt2-medium-xxx.checkpoint \
    --save_dir {huggingface's model repo directory}
~~~~

3. Validate the created files by running:
~~~~
python -m task.pretrain_gpt2.check_huggingface \
    --model_dir {huggingface's model repo directory}
~~~~

4. Add files, commit, and push to your Huggingface repo.

### Customize your GPT-2 training

Check available arguments of GPT-2 training script by running:
~~~~
python -m task.pretrain_gpt2.train --help
~~~~

---

## Train `japanese-roberta-base` from scratch

Assume you have finished the data construction process as described above, run the following command to train a base-sized Japanese RoBERTa on, for example, 8 V100 GPUs:

~~~~
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 python -m task.pretrain_roberta.train \
    --n_gpus 8 \
    --save_model True \
    --enable_log True \
    --model_size base \
    --model_config_filepath model/roberta-ja-base-config.json \
    --batch_size 32 \
    --eval_batch_size 32 \
    --n_training_steps 3000000 \
    --n_accum_steps 16 \
    --init_lr 0.0006
~~~~

---

## License

[The Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0)
