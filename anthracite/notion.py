import time
from google.cloud import firestore
from language_analysis.language_analysis import sentiment_analysis

from anthracite.ticker import check_for_ticker
# from utils import settings


def process_notion(notion, ticker_list):
    found_tickers = check_for_ticker(notion.text, ticker_list)
    if found_tickers is None:
        return
    notion.tickers = list(map(lambda x: x.ticker, found_tickers))
    # sentiment = sentiment_analysis(notion.text)
    # notion.sentiment = sentiment.sentiment
    # notion.magnitude = sentiment.magnitude
    # notion.upload()
    return notion
