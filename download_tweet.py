from __future__ import annotations

import os
import time
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
    for tweet in tweepy.Paginator(
        client.get_users_tweets,
        id=user_id,
        max_results=max_tweets,
        exclude=["retweets", "replies"],
    ).flatten(limit=max_tweets):

        # if tweet includes media, skip it
        if "http" in tweet.text:
            continue

        tweets.append("<|startoftext|>" + tweet.text + "<|endoftext|>")

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
        "-max",
        "--max_tweets",
        type=int,
        help="Max number of tweets to download",
        default=100,
        dest="max_tweets",
    )
    args = argparser.parse_args()

    # Load .env file and get bearer token
    load_dotenv()

    auth_info = AuthenticationInfo(
        api_key=os.getenv("API_KEY"),
        api_secret_key=os.getenv("API_SECRET_KEY"),
        bearer_token=os.getenv("BEARER_TOKEN"),
    )

    tweets = get_tweets_from_user(
        auth_info,
        user_id=args.user_id,
        user_name=args.user_name,
        max_tweets=args.max_tweets,
    )

    with open("tweets/tweets.txt", "w") as f:
        tweets = "\n".join(tweets)
        print(tweets)
        f.write(tweets)


if __name__ == "__main__":
    main()
