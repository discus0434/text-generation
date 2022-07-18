from __future__ import annotations

import os
import time
from datetime import datetime
from pathlib import Path
import argparse
from dataclasses import dataclass

import tweepy
from dotenv import load_dotenv


@dataclass
class AuthenticationInfo:
    api_key: str
    api_secret_key: str
    bearer_token: str


def get_tweets_from_user(
    auth_info: AuthenticationInfo,
    *,
    user_id: int | None,
    user_name: str | None,
    max_tweets: int = 100,
) -> list[str]:

    client = tweepy.Client(
        consumer_key=auth_info.api_key,
        consumer_secret=auth_info.api_secret_key,
        bearer_token=auth_info.bearer_token,
    )

    if user_id is None:
        user_id = client.get_user(username=user_name).data["id"]

    tweets = []
    oldest_tweet_id = None
    n_roop = max_tweets // 200

    try:
        for roop_idx in range(n_roop):
            for tweet in tweepy.Paginator(
                client.get_users_tweets,
                id=user_id,
                max_results=100,
                exclude=["retweets"],
                until_id=oldest_tweet_id,
            ).flatten(limit=200):

                # if tweet includes media or mention, skip it
                if "http" in tweet.text:
                    continue
                if tweet.text.startswith("@"):
                    continue

                oldest_tweet_id = tweet.id
                tweets.append(tweet.text + "<|endoftext|>")
            print(f"roop {roop_idx} has been finished. wait for {900 // 4} secs...")
            time.sleep(900 // 4)

        return tweets

    except KeyboardInterrupt:

        return tweets


def main():
    # Get arguments from command line
    argparser = argparse.ArgumentParser(description="Download tweets from Twitter")
    argparser.add_argument(
        "-uid",
        "--user_id",
        type=int,
        help="User ID",
        required=False,
        default=None,
        dest="user_id",
    )
    argparser.add_argument(
        "-u",
        "--user_name",
        type=str,
        help="Twitter user name",
        required=False,
        default="POTUS",
        dest="user_name",
    )
    argparser.add_argument(
        "-o",
        "--output_dir",
        type=str,
        help="Output dir",
        default="sample_texts",
        dest="output_dir",
    )
    argparser.add_argument(
        "-max",
        "--max_tweets",
        type=int,
        help="Max number of tweets to download. Value must be multiple of 200",
        default=200,
        dest="max_tweets",
    )
    args = argparser.parse_args()

    # Load .env file and get bearer token
    load_dotenv()

    auth_info = AuthenticationInfo(
        api_key=os.getenv("TEINEI_API_KEY"),
        api_secret_key=os.getenv("TEINEI_API_SECRET_KEY"),
        bearer_token=os.getenv("TEINEI_BEARER_TOKEN"),
    )

    tweets = get_tweets_from_user(
        auth_info,
        user_id=args.user_id,
        user_name=args.user_name,
        max_tweets=args.max_tweets,
    )

    today = datetime.strftime(datetime.today(), '%Y-%m-%d')

    if not os.path.exists(Path(args.output_dir)):
        os.makedirs(Path(args.output_dir), exist_ok=True)

    with open(Path(args.output_dir) / f"{today}_{args.user_name}_{args.max_tweets}.txt", "w") as f:
        tweets = "\n".join(tweets)
        print(tweets)
        f.write(tweets)


if __name__ == "__main__":
    main()
