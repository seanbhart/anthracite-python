import os
import logging
import praw
from dotenv import load_dotenv


def update(subreddit: str, recency: str):
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )
    subreddit = reddit.subreddit(subreddit)

    for submission in subreddit.top(recency):
        # print(dir(submission))
        # print(vars(submission))
        data = {
            'reddit_id': submission.id,
            'title': submission.title,
            'text': submission.selftext
        }

        if submission.num_comments < 90000:
            submission.comments.replace_more(limit=2)
            for top_level_comment in submission.comments.list():
                # print(top_level_comment.body)
                print(top_level_comment.__dict__)
                break
            break


if __name__ == '__main__':
    load_dotenv(dotenv_path="../local/.env")
    update(subreddit="wallstreetbets", recency="day")
