import logging
from dotenv import load_dotenv

from anthracite import ticker
import reddit.model as rmodel
from reddit import reddit as red
from language_analysis.language_analysis import sentiment_analysis


def get_reddit_top_breadth(subreddit: str, recency: str, layers: int):
    print(f"GET SUBREDDIT {subreddit} TOP POSTS BY BREADTH IN LAST {recency}")
    ticker_list = ticker.get_tickers()
    try:
        for submission in red.get_top(subreddit=subreddit, recency=recency):
            # if submission.stickied:
            #     continue
            print(submission.id)

            # Reddit cannot serve too many comments
            if submission.num_comments > 90000:
                continue

            submission.comments.replace_more(limit=layers)
            for comment in submission.comments.list():
                notion2 = rmodel.notion_from_comment(comment.__dict__)
                found_tickers2 = ticker.check_for_ticker(notion2.text, ticker_list)
                if found_tickers2 is not None:
                    notion2.tickers = list(map(lambda x: x.ticker, found_tickers2))
                    sentiment = sentiment_analysis(notion2.text)
                    notion2.sentiment = sentiment.sentiment
                    notion2.magnitude = sentiment.magnitude
                    notion2.upload()

            notion = rmodel.notion_from_submission(submission.__dict__)
            found_tickers = ticker.check_for_ticker(notion.text, ticker_list)
            if found_tickers is not None:
                notion.tickers = list(map(lambda x: x.ticker, found_tickers))
                sentiment = sentiment_analysis(notion.text)
                notion.sentiment = sentiment.sentiment
                notion.magnitude = sentiment.magnitude
                notion.upload()

    except Exception as error:
        logging.error(f"Exception: {error}")


def main():
    get_reddit_top_breadth(subreddit="Wallstreetbets", recency="hour", layers=10)
    get_reddit_top_breadth(subreddit="Wallstreetbetsnew", recency="hour", layers=10)
    get_reddit_top_breadth(subreddit="StonkTraders", recency="hour", layers=10)
    get_reddit_top_breadth(subreddit="pennystocks", recency="hour", layers=10)
    get_reddit_top_breadth(subreddit="RobinHoodPennyStocks", recency="hour", layers=10)
    get_reddit_top_breadth(subreddit="Bitcoin", recency="hour", layers=10)
    get_reddit_top_breadth(subreddit="Bitcoincash", recency="hour", layers=10)
    get_reddit_top_breadth(subreddit="BitcoinMarkets", recency="hour", layers=10)
    get_reddit_top_breadth(subreddit="btc", recency="hour", layers=10)
    get_reddit_top_breadth(subreddit="ethereum", recency="hour", layers=10)
    get_reddit_top_breadth(subreddit="ethtrader", recency="hour", layers=10)
    get_reddit_top_breadth(subreddit="litecoin", recency="hour", layers=10)
    get_reddit_top_breadth(subreddit="LitecoinMarkets", recency="hour", layers=10)
    get_reddit_top_breadth(subreddit="dogecoin", recency="hour", layers=10)
    # red.get_reddit_top_depth(subreddit="wallstreetbets", recency="hour", layers=3)


debug = False
if __name__ == '__main__':
    load_dotenv(dotenv_path="./local/.env")
    logging.basicConfig(format='[%(asctime)s] {%(filename)s:%(lineno)d} - %(name)s - %(levelname)s - %(message)s')
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    main()
