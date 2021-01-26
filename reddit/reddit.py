import os
import logging
import praw
from dotenv import load_dotenv

from anthracite import anthracite
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
    return reddit.subreddit(subreddit).top(recency)


def get_replies(comment, ticker_list):
    comment_list = []
    notion_list = []
    for r1 in comment.replies:
        notion = notion_from_comment(r1.__dict__)
        comment_list.append(r1)
        notion_p = anthracite.process_notion(notion, ticker_list)
        if notion_p:
            notion_list.append(notion_p)
        reply_comments, reply_notions = get_replies(r1, ticker_list)
        for r2 in reply_comments:
            notion2 = notion_from_comment(r2.__dict__)
            comment_list.append(r2)
            notion_p2 = anthracite.process_notion(notion2, ticker_list)
            if notion_p2:
                notion_list.append(notion_p2)
    return comment_list, notion_list


if __name__ == '__main__':
    load_dotenv(dotenv_path="../local/.env")
    update(subreddit="wallstreetbets", recency="day")
