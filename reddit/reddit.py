import os
import logging
import praw
from dotenv import load_dotenv

from model import notion_from_submission, notion_from_comment


def update(subreddit: str, recency: str):
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )
    subreddit = reddit.subreddit(subreddit)

    for submission in subreddit.top(recency):
        notion_from_submission(submission.__dict__).upload()

        # Reddit cannot serve too many comments
        if submission.num_comments > 90000:
            continue

        submission.comments.replace_more(limit=2)
        for comment in submission.comments.list():
            notion_from_comment(comment.__dict__).upload()


if __name__ == '__main__':
    load_dotenv(dotenv_path="../local/.env")
    update(subreddit="wallstreetbets", recency="day")
