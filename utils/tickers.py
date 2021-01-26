import csv
from google.cloud import firestore

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
        })
        # }, merge=True)


def get_tickers() -> list:
    client = firestore.Client()
    docs = client.collection(settings.Firestore.collection_ticker) \
        .where(u'status', u'==', 1) \
        .stream()
    tickers = []
    for doc in docs:
        tickers.append(doc.to_dict())
    return tickers


if __name__ == '__main__':
    # load_tickers('../data/tickers.csv')
    print(get_tickers())
