import logging
from statistics import mean
# from prawcore.exceptions import Forbidden, ResponseException
# from dotenv import load_dotenv
from celery import Celery

from anthracite import ticker
from reddit.model import notion_from_submission, notion_from_comment
from reddit.reddit_processing import get_top, get_replies_with_sentiment
from language_analysis.language_analysis import sentiment_analysis


BROKER_URL = 'redis://localhost:6379/0'
app = Celery('reddit', broker=BROKER_URL)


@app.task
def get_reddit_top_breadth(subreddit: str, recency: str, layers: int):
    print(f"GET SUBREDDIT {subreddit} TOP POSTS BY BREADTH IN LAST {recency}")
    ticker_list = ticker.get_tickers()
    try:
        for submission in get_top(subreddit=subreddit, recency=recency):
            # if submission.stickied:
            #     continue
            print(submission.id)

            # Reddit cannot serve too many comments
            if submission.num_comments > 90000:
                continue

            submission.comments.replace_more(limit=layers)
            for comment in submission.comments.list():
                notion2 = notion_from_comment(comment.__dict__)
                found_tickers2 = ticker.check_for_ticker(notion2.text, ticker_list)
                if found_tickers2 is not None:
                    notion2.tickers = list(map(lambda x: x.ticker, found_tickers2))
                    # sentiment = sentiment_analysis(notion2.text)
                    # notion2.sentiment = sentiment.sentiment
                    # notion2.magnitude = sentiment.magnitude
                    notion2.upload()

            notion = notion_from_submission(submission.__dict__)
            found_tickers = ticker.check_for_ticker(notion.text, ticker_list)
            if found_tickers is not None:
                notion.tickers = list(map(lambda x: x.ticker, found_tickers))
                # sentiment = sentiment_analysis(notion.text)
                # notion.sentiment = sentiment.sentiment
                # notion.magnitude = sentiment.magnitude
                notion.upload()

    except Exception as error:
        logging.error(f"Exception: {error}")


def get_reddit_top_depth(subreddit: str, recency: str, layers: int):
    print(f"GET SUBREDDIT {subreddit} TOP POSTS BY DEPTH IN LAST {recency}")
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
                sentiment = sentiment_analysis(notion.text)
                notion.sentiment = sentiment.sentiment
                notion.magnitude = sentiment.magnitude
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
                # print(f"submission comment: {comment}")
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
                print(f"NOTION: {notion_p.host_id}: S: {notion_p.sentiment}, M: {notion_p.magnitude} \
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
    print("reddit start")
    # load_dotenv(dotenv_path="../local/.env")
