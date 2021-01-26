import os
import logging
import praw
from dotenv import load_dotenv

from reddit.model import notion_from_submission, notion_from_comment
from utils import tickers


def update(subreddit: str, recency: str):
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )
    subreddit = reddit.subreddit(subreddit)

    ticker_list = tickers.get_tickers()
    i = 0
    for submission in subreddit.top(recency):
        i += 1
        # notion_from_submission(submission.__dict__).upload()
        notion = notion_from_submission(submission.__dict__)
        found_tickers = tickers.check_for_ticker(notion.text, ticker_list)

        # Reddit cannot serve too many comments
        if submission.num_comments > 90000:
            continue

        submission.comments.replace_more(limit=2)
        for comment in submission.comments.list():
            # notion_from_comment(comment.__dict__).upload()
            notion2 = notion_from_comment(comment.__dict__)
            found_tickers = tickers.check_for_ticker(notion2.text, ticker_list)
    print(i)


def get_top(subreddit: str, recency: str):
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )
    subreddit = reddit.subreddit(subreddit)
    return subreddit.top(recency)


if __name__ == '__main__':
    load_dotenv(dotenv_path="../local/.env")
    update(subreddit="wallstreetbets", recency="day")
