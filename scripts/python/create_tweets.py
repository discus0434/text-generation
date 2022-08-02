from __future__ import annotations

import os
import sys
import re
import time
import random
import glob
import argparse
import subprocess
from datetime import datetime
from dataclasses import dataclass

import tweepy
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from config import NG_WORDS

load_dotenv()

NUM_TWEETS_PER_DAY = 72


@dataclass
class AuthenticationInfo:
    api_key: str = ("",)
    api_secret_key: str = ("",)
    bearer_token: str = ("",)
    access_token: str = ("",)
    access_token_secret: str = ("",)


def finetune(
    src_dir: str = "sample_texts",
    dst_file: str = "finetune",
    run_name: str = "gpt2ja-finetune-small",
) -> None:

    # Encode a dataset
    subprocess.run(
        f"python gpt2-japanese/encode_bpe.py --src_dir {src_dir} --dst_file {dst_file}",
        shell=True,
    )

    # Fine-Tune
    subprocess.run(
        f"python gpt2-japanese/run_finetune.py \
        --base_model gpt2ja-small \
        --dataset {dst_file}.npz \
        --run_name {run_name}",
        shell=True,
    )

    # Remove interim files
    subprocess.run(f"rm {dst_file}.npz", shell=True)
    subprocess.run("for i in $(seq 0 7); do rm tmp$i.pkl; done", shell=True)

    return None


def generate(
    model: str = "checkpoints/gpt2ja-finetune-small",
    num_generate: int = 1,
    temperature: float = 1.0,
    min_length: int = 10,
    max_length: int = 139,
    output_file: str = "dist/dist.txt",
    context: str = "<|endoftext|>",
) -> str:

    while True:
        generated = subprocess.run(
            f"TF_CPP_MIN_LOG_LEVEL=3 \
            python gpt2-japanese/gpt2-generate.py \
            --model {model} \
            --num_generate {num_generate} \
            --temperature {temperature} \
            --min_length {min_length} \
            --max_length {max_length} \
            --output_file {output_file} \
            --context={context}",
            shell=True,
            capture_output=True,
        ).stdout.decode()

        if not bool(re.search("|".join(NG_WORDS), generated)):
            break

    return generated


def post_tweet(
    client: tweepy.Client,
    text: str,
    score: str,
    model: str,
) -> None:
    json = {}

    # If score has no value, disable poll-making and scoring
    if not score == "":
        poll_or_not = random.randint(0, 100)
        if poll_or_not >= 95:
            options = []
            for _ in range(3):
                options.append(
                    generate(
                        model=model,
                        context=text,
                        num_generate=1,
                        output_file="dist/dist.txt",
                        min_length=5,
                        max_length=19,
                    )
                )

        json["poll"] = {"options": options, "duration_minutes": 30}

        json["text"] = text

    else:
        json["text"] = text

    with open("./dist/hist.txt", "a") as f:
        f.write(
            "=========\n" + text + "=========\n" + f"\n score: {score}" + "=========\n"
        )

    return client._make_request("POST", "/2/tweets", json=json, user_auth=True)


def create_custom_tweets(
    auth_info: AuthenticationInfo,
    model: str | None = None,
    no_post: bool = False,
) -> tuple[str, float] | None:

    client = tweepy.Client(
        consumer_key=auth_info.api_key,
        consumer_secret=auth_info.api_secret_key,
        access_token=auth_info.access_token,
        access_token_secret=auth_info.access_token_secret,
    )

    if model is None:
        # If model is not specified, use the oldest one
        try:
            model = glob.glob("./checkpoints/*small")[0]

        # If a fine-tuned GPT-2-ja-small does not exist, make it
        except IndexError:
            today = datetime.strftime(datetime.today(), "%Y-%m-%d")
            finetune(
                dst_file=f"{today}-finetune",
                run_name=f"gpt2ja-{today}-finetune-small",
            )
    else:
        if not os.path.exists(f"./checkpoints/{model}"):
            finetune(
                dst_file=f"{model}-finetune",
                run_name=model,
            )

        model = f"./checkpoints/{model}"

    while True:
        generated_text = generate(
            model=model,
            context="",
            num_generate=1,
            output_file="dist/dist.txt",
        )

        score = (
            subprocess.run(
                f"python gpt2-japanese/gpt2-score.py \
                    dist/dist.txt \
                    --model {model} \
                    --exclude-end",
                shell=True,
                capture_output=True,
            )
            .stdout.decode()
            .split("\t")[-1]
            .strip()
        )

        if float(score) > -150:
            break

    # If no_post is True, print texts and do early return
    if no_post:
        print(generated_text, float(score))
        return generated_text, float(score)

    post_tweet(client, text=generated_text, score=score, model=model)


def main():

    # Get arguments from command line
    argparser = argparse.ArgumentParser(description="Download tweets from Twitter")
    argparser.add_argument(
        "-m",
        "--model",
        type=str,
        help="Model Name",
        required=False,
        default=None,
        dest="model",
    )
    argparser.add_argument("--no_post", action="store_true")
    args = argparser.parse_args()

    # Get auth tokens from .env file
    auth_info = AuthenticationInfo(
        api_key=os.getenv("API_KEY"),
        api_secret_key=os.getenv("API_SECRET_KEY"),
        access_token=os.getenv("ACCESS_TOKEN"),
        access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
    )

    # Run for a year
    for _ in range(NUM_TWEETS_PER_DAY * 365):

        # Generate a tweet and post it
        create_custom_tweets(
            auth_info=auth_info, model=args.model, no_post=args.no_post
        )

        # Sleep 30 min
        time.sleep(86400 // NUM_TWEETS_PER_DAY)


if __name__ == "__main__":
    main()
