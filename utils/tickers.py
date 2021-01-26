import csv
from google.cloud import firestore
from PyDictionary import PyDictionary

from utils import settings


class Ticker:
    def __init__(self,
                 ticker: str,
                 status: int,
                 name: str,
                 exchange: str,
                 ):
        self.ticker = ticker
        self.status = status
        self.name = name
        self.exchange = exchange

    def __init__(self, data: dict):
        self.ticker = data['ticker']
        self.status = data['status']
        self.name = data['name']
        self.exchange = data['exchange']


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


def filter_tickers():
    client = firestore.Client()
    docs = client.collection(settings.Firestore.collection_ticker) \
        .where(u'status', u'==', 1) \
        .stream()
    for doc in docs:
        ticker_dict = doc.to_dict()
        dictionary = PyDictionary()
        meaning = dictionary.meaning(ticker_dict['ticker'], disable_errors=True)
        if meaning is not None or len(ticker_dict['ticker']) < 2:
            # print(f"{ticker_dict['ticker']}: {dictionary.meaning(ticker_dict['ticker'])}")
            ticker_doc = client.collection(settings.Firestore.collection_ticker).document(doc.id)
            ticker_doc.set({
                u'status': 0
            }, merge=True)


def get_tickers() -> list:
    client = firestore.Client()
    docs = client.collection(settings.Firestore.collection_ticker) \
        .where(u'status', u'==', 1) \
        .stream()
    tickers = []
    for doc in docs:
        tickers.append(Ticker(doc.to_dict()))
    return tickers


def check_for_ticker(text: str, tickers: [Ticker]) -> [Ticker]:
    if len(text) < 1:
        return None
    tickers_found = []
    for t in tickers:
        t_index = text.rfind(" " + t.ticker + " ")
        t_index2 = text.rfind("$" + t.ticker + " ")
        if t_index >= 0 or t_index2 >= 0:
            tickers_found.append(t)
    if len(tickers_found) == 0:
        return None
    return tickers_found


if __name__ == '__main__':
    # load_tickers('../data/tickers.csv')
    # print(get_tickers())
    filter_tickers()
