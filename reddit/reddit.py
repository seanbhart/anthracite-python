import logging
from google.cloud import firestore
from statistics import mean
# from prawcore.exceptions import Forbidden, ResponseException
# from dotenv import load_dotenv
# from celery import Celery

from anthracite import ticker
from reddit.model import notion_from_submission, notion_from_comment
from reddit.reddit_processing import get_top, get_replies_with_sentiment
from utils import settings


def process_reddit_breadth() -> None:
    """Recall the subreddits to pull along with their request
    settings. Process all subreddits with a status of 1 (active).
    Traverses comments by breadth.
    """
    client = firestore.Client()
    doc = client.collection(settings.Firestore.collection_host) \
        .document('reddit') \
        .get()
    reddit_doc = doc.to_dict()
    for subreddit in reddit_doc['subreddits']:
        if subreddit['status'] == 1:
            process_subreddit_top_breadth(subreddit=subreddit['subreddit'],
                                          recency=subreddit['recency'],
                                          layers=subreddit['layers']
                                          )
    logging.warning("REDDIT BREADTH COMPLETE")


# BROKER_URL = 'redis://localhost:6379/0'
# app = Celery('reddit', broker=BROKER_URL)


# @app.task
def process_subreddit_top_breadth(subreddit: str, recency: str, layers: int) -> None:
    """Request top subreddit submissions and comments by traversing comments by
    breadth (all 1st layer comments, all 2nd layer comments, etc.). This
    prevents aggregating data up comment layers, but is more likely to gather
    high quality posts faster. Depth requests (especially too deep) seem to
    bog down in low quality posts.
    """
    logging.info(f"GET SUBREDDIT {subreddit} TOP POSTS BY BREADTH IN LAST {recency}")
    ticker_list = ticker.get_tickers()
    try:
        for submission in get_top(subreddit=subreddit, recency=recency):
            # if submission.stickied:
            #     continue
            logging.info(f"processing submission: {submission.id}")

            # Reddit cannot serve too many comments
            if submission.num_comments > 90000:
                continue

            submission.comments.replace_more(limit=layers)
            for comment in submission.comments.list():
                notion2 = notion_from_comment(comment.__dict__)
                found_tickers2 = ticker.check_for_ticker(notion2.text, ticker_list)
                if found_tickers2 is not None:
                    notion2.tickers = list(map(lambda x: x.ticker, found_tickers2))
                    notion2.upload()

            notion = notion_from_submission(submission.__dict__)
            found_tickers = ticker.check_for_ticker(notion.text, ticker_list)
            if found_tickers is not None:
                notion.tickers = list(map(lambda x: x.ticker, found_tickers))
                notion.upload()

    except Exception as error:
        logging.error(f"Exception: {error}")


def process_subreddit_top_depth(subreddit: str, recency: str, layers: int) -> None:
    """Request top subreddit submissions and comments by traversing comments by
    depth (stair-step down each comment thread). This allows aggregating data up
    comment layers, like sentiment and total response counts, but it seems to bog
    down in low quality posts, especially if dug too deep.

    CAUTION: Sentiment analysis (especially Google Natural Language) can be expensive,
    and costs should be considered when deciding to aggregate statistics up comment layers.
    """
    logging.info(f"GET SUBREDDIT {subreddit} TOP POSTS BY DEPTH IN LAST {recency}")
    ticker_list = ticker.get_tickers()
    notions = []
    i = 0
    try:
        for submission in get_top(subreddit=subreddit, recency=recency):
            # if submission.stickied:
            #     continue
            notion = notion_from_submission(submission.__dict__)
            found_tickers = ticker.check_for_ticker(notion.text, ticker_list)
            if found_tickers is not None:
                notion.tickers = list(map(lambda x: x.ticker, found_tickers))
                # sentiment = sentiment_analysis(notion.text)
                # notion.sentiment = sentiment.sentiment
                # notion.magnitude = sentiment.magnitude
                notion.upload()
            notion_p = notion.process_notion(notion, ticker_list)
            if notion_p:
                notions.append(notion_p)

            # Reddit cannot serve too many comments
            if submission.num_comments > 90000:
                continue

            sentiment_all = []
            magnitude_all = []
            submission.comments.replace_more(limit=layers)
            for comment in submission.comments:
                notion2 = notion_from_comment(comment.__dict__)
                # logging.info(f"submission comment: {comment}")
                notion_p2 = notion.process_notion(notion2, ticker_list)
                if notion_p2:
                    notions.append(notion_p2)
                _, comment_notions, sentiment_c, magnitude_c = get_replies_with_sentiment(comment, ticker_list)
                notions.extend(comment_notions)
                if sentiment_c:
                    sentiment_all.append(sentiment_c)
                if magnitude_c:
                    magnitude_all.append(magnitude_c)

            if notion_p and len(sentiment_all) > 1 and len(magnitude_all) > 1:
                sentiment_adj = mean([notion_p.sentiment, mean(sentiment_all)])
                magnitude_adj = mean([notion_p.magnitude, mean(magnitude_all)])
                logging.info(f"NOTION: {notion_p.host_id}: S: {notion_p.sentiment}, M: {notion_p.magnitude} \
                        --- S: {sentiment_adj}, M: {magnitude_adj} --- TEXT: {notion_p.text}")
            print(i)
            i += 1
            # if i > 5:
            #     break
    except Exception as error:
        logging.error(f"Exception: {error}")
    # for n in notions:
    #     print(n)


if __name__ == '__main__':
    logging.info("reddit start")
    # load_dotenv(dotenv_path="../local/.env")
