import csv
from google.cloud import firestore
from PyDictionary import PyDictionary

from anthracite.model import Ticker, Notion
from utils import settings


def read_tickers(filepath: str) -> list:
    with open(filepath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        tickers = []
        line_count = 0
        for row in csv_reader:
            # Skip the header row
            if line_count > 0:
                ticker = {
                    'ticker': row[0],
                    'name': row[1],
                    'exchange': row[3],
                }
                tickers.append(ticker)
            line_count += 1
        return tickers


def load_tickers(filepath: str):
    tickers = read_tickers(filepath)
    client = firestore.Client()
    for t in tickers:
        ticker_doc = client.collection(settings.Firestore.collection_ticker).document()
        ticker_doc.set({
            u'status': 1,
            u'ticker': t['ticker'],
            u'name': t['name'],
            u'exchange': t['exchange'],
        }, merge=True)


def transform_tickers():
    client = firestore.Client()
    docs = client.collection(settings.Firestore.collection_ticker) \
        .where(u'status', u'==', 0) \
        .get()
    for doc in docs:
        ticker_doc = client.collection(settings.Firestore.collection_ticker).document(doc.id)
        ticker_doc.set({
            u'status': 2
        }, merge=True)


def filter_tickers():
    client = firestore.Client()
    docs = client.collection(settings.Firestore.collection_ticker) \
        .where(u'status', u'==', 1) \
        .stream()
    for doc in docs:
        ticker = Ticker(data=doc.to_dict())
        meaning = ticker_meaning(ticker)
        if meaning is not None or len(ticker.ticker) < 2:
            print(f"FILTERING OUT TICKER: {ticker.ticker}")
            ticker_doc = client.collection(settings.Firestore.collection_ticker).document(doc.id)
            ticker_doc.set({
                u'status': 2
            }, merge=True)


def ticker_meaning(ticker: Ticker):
    dictionary = PyDictionary()
    return dictionary.meaning(ticker.ticker, disable_errors=True)


def get_tickers() -> list:
    client = firestore.Client()
    docs = client.collection(settings.Firestore.collection_ticker) \
        .where(u'status', u'>', 0) \
        .stream()
    tickers = []
    for doc in docs:
        tickers.append(Ticker(doc.to_dict()))
    return list(set(tickers))


def check_for_ticker(text: str, tickers: [Ticker]) -> [Ticker]:
    if len(text) < 1:
        return None
    tickers_found = []
    for t in tickers:
        if t.status == 1:
            if text.rfind(" " + t.ticker + " ") >= 0 or text.rfind("$" + t.ticker + " ") >= 0:
                tickers_found.append(t)
        elif t.status == 2:
            if text.rfind("$" + t.ticker + " ") >= 0:
                tickers_found.append(t)
    if len(tickers_found) == 0:
        return None
    return tickers_found


if __name__ == '__main__':
    # load_tickers('../data/tickers.csv')
    # print(get_tickers())
    filter_tickers()
    # transform_tickers()

