import os
import time
import json
import logging
import argparse
import warnings
from dataclasses import dataclass

warnings.simplefilter("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_DETERMINISTIC_OPS"] = "0"

import tqdm
import numpy as np
from tensorflow.core.protobuf import rewriter_config_pb2
import tensorflow._api.v2.compat.v1 as tf

tf.get_logger().setLevel(logging.ERROR)


from .model import modeling
from .model.modeling import BertConfig, BertModel
from .run_finetune import get_masked_lm_output, get_next_sentence_output
from .encode_bpe import BPEEncoder_ja


@dataclass
class Args:
    model: str = "roBERTa-ja_base",
    context: list[str] = [],
    split_tag: str = "",
    gpu: str = b"0",
    output_max: bool = False,
    value_only: bool = True,


def bert_scoring(args):
    with open(args.model + "/hparams.json") as f:
        bert_config_params = json.load(f)
    bert_config = BertConfig(**bert_config_params)
    vocab_size = bert_config_params["vocab_size"]
    max_seq_length = bert_config_params["max_position_embeddings"]
    EOT_TOKEN = vocab_size - 4
    MASK_TOKEN = vocab_size - 3
    CLS_TOKEN = vocab_size - 2
    SEP_TOKEN = vocab_size - 1

    config = tf.ConfigProto()
    config.gpu_options.visible_device_list = args.gpu

    with tf.Session(config=config, graph=tf.Graph()) as sess:
        input_ids = tf.placeholder(tf.int32, [None, None])
        input_mask = tf.placeholder(tf.int32, [None, None])
        segment_ids = tf.placeholder(tf.int32, [None, None])
        masked_lm_positions = tf.placeholder(tf.int32, [None, None])
        masked_lm_ids = tf.placeholder(tf.int32, [None, None])
        masked_lm_weights = tf.placeholder(tf.float32, [None, None])
        next_sentence_labels = tf.placeholder(tf.int32, [None])

        model = BertModel(
            config=bert_config,
            is_training=False,
            input_ids=input_ids,
            input_mask=input_mask,
            token_type_ids=segment_ids,
            use_one_hot_embeddings=False,
        )

        output = model.get_sequence_output()
        (_, _, log_prob) = get_masked_lm_output(
            bert_config,
            model.get_sequence_output(),
            model.get_embedding_table(),
            masked_lm_positions,
            masked_lm_ids,
            masked_lm_weights,
        )
        (_, _, _) = get_next_sentence_output(
            bert_config, model.get_pooled_output(), next_sentence_labels
        )

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(args.model)
        saver.restore(sess, ckpt)

        with open("RoBERTa_japanese/ja-bpe.txt", encoding="utf-8") as f:
            bpe = f.read().split("\n")

        with open("RoBERTa_japanese/emoji.json", encoding="utf-8") as f:
            emoji = json.loads(f.read())

        enc = BPEEncoder_ja(bpe, emoji)

        if isinstance(args.context, str):
            context_list = [args.context]
        else:
            context_list = args.context

        bert_score = []
        for each_context in context_list:
            if args.split_tag != "":
                contexts = each_context.split(args.split_tag)
            else:
                contexts = [each_context]
            _input_ids = []
            _input_masks = []
            _segments = []
            _mask_positions = []
            for context in contexts:
                context_tokens = enc.encode(context)
                context_tokens = context_tokens[: max_seq_length - 3]
                inputs = []
                inputs.append(CLS_TOKEN)
                inputs.extend(context_tokens)
                inputs.append(EOT_TOKEN)
                inputs.append(SEP_TOKEN)  # [CLS]+tokens+<|endoftext|>+[SEP]
                input_masks = [1] * len(inputs)
                segments = [1] * len(inputs)
                while len(inputs) < max_seq_length:
                    inputs.append(0)
                    input_masks.append(0)
                    segments.append(1)
                _input_ids.append(inputs)
                _input_masks.append(input_masks)
                _segments.append(segments)
                mask_positions = list(range(len(inputs)))
                _mask_positions.append(mask_positions)

            max_mask_count = np.max([len(c) for c in _mask_positions])
            for p in range(len(_mask_positions)):
                q = len(_mask_positions[p])
                if q < max_mask_count:
                    _mask_positions[p].extend([0] * (max_mask_count - q))

            prob = sess.run(
                log_prob,
                feed_dict={
                    input_ids: _input_ids,
                    input_mask: _input_masks,
                    segment_ids: _segments,
                    masked_lm_positions: _mask_positions,
                    masked_lm_ids: np.zeros((len(_input_ids), max_mask_count), dtype=np.int32),
                    masked_lm_weights: np.ones(
                        (len(_input_ids), max_mask_count), dtype=np.float32
                    ),
                    next_sentence_labels: np.zeros((len(_input_ids),), dtype=np.int32),
                },
            )
            results = []
            for i in range(len(_input_ids)):
                result_lines = []
                for j in range(1, len(_input_ids[i])):
                    if _input_ids[i][j] < EOT_TOKEN:
                        score = prob[j][_input_ids[i][j]]
                        word = enc.decode([_input_ids[i][j]])
                        maxword = enc.decode([np.argmax(prob[j])])
                        if args.output_max:
                            result_lines.append(f"{score}\t{word}\t{maxword}")
                        elif args.value_only:
                            result_lines.append(score)
                        else:
                            result_lines.append(f"{score}\t{word}")
                    else:
                        break
                if args.value_only:
                    results.append(sum(result_lines))
                else:
                    results.append("\n".join(result_lines))
            if args.value_only:
                print(sum(results))
                bert_score.append(sum(results))
            else:
                print("=================\n".join(results))
    if args.value_only:
        return bert_score

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="RoBERTa-ja_small")
    parser.add_argument("--context", dest="context", nargs="*", type=str, required=True)
    parser.add_argument("--split_tag", type=str, default="")
    parser.add_argument("--gpu", default="0", help="visible gpu number.")
    parser.add_argument("--output_max", default=False, action="store_true")
    parser.add_argument("--value_only", default=False, action="store_true")
    args = parser.parse_args()

    bert_scoring(args)