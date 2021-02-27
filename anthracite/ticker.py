import csv
import logging
import requests
from requests.exceptions import HTTPError
import time
from google.cloud import firestore
from PyDictionary import PyDictionary

from anthracite.model import Ticker, Notion
from utils import settings


def read_tickers(filepath: str) -> list:
    """Load Ticker data from a CSV file and
    return in a filtered list format.
    """
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
    """Load Tickers from a CSV file into the database.

    CAUTION: This data format might be deprecated.
    """
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
    """A standalone function to refactor Tickers already in
    the database with a new status indicator.
    """
    client = firestore.Client()
    docs = client.collection(settings.Firestore.collection_ticker) \
        .where(u'status', u'==', 0) \
        .get()
    logging.info(f"(transform_tickers) FIREBASE READ TICKER DOC COUNT: {len(docs)}")
    for doc in docs:
        ticker_doc = client.collection(settings.Firestore.collection_ticker).document(doc.id)
        ticker_doc.set({
            u'status': 2
        }, merge=True)


def fill_settings_tickers():
    """A standalone function to fill the settings collection
    with a single doc filled with all tickers (for use
    referencing tickers without reading all full ticker docs).
    """
    client = firestore.Client()
    docs = client.collection(settings.Firestore.collection_ticker) \
        .where(u'status', u'>', 0) \
        .get()
    logging.info(f"(full_settings_tickers) FIREBASE READ TICKER DOC COUNT: {len(docs)}")
    ticker_symbols = []
    for doc in docs:
        ticker = Ticker(data=doc.to_dict())
        ticker_symbols.append(ticker.ticker)
    ticker_symbols.sort()
    # print(len(ticker_symbols))
    # print(ticker_symbols)
    ticker_doc = client.collection(settings.Firestore.collection_settings).document("tickers")
    ticker_doc.set({"all": ticker_symbols})


def filter_tickers():
    """A standalone function to process Tickers already in
    the database. Make changes to the function for custom
    filtering as needed. (e.g. Use the dictionary lookup
    to remove Tickers likely to be caught with common words.)
    """
    client = firestore.Client()
    docs = client.collection(settings.Firestore.collection_ticker) \
        .where(u'status', u'==', 1) \
        .get()
    logging.info(f"(filter_tickers) FIREBASE READ TICKER DOC COUNT: {len(docs)}")
    for doc in docs:
        ticker = Ticker(data=doc.to_dict())
        meaning = ticker_meaning(ticker)
        if meaning is not None or len(ticker.ticker) < 2:
            logging.info(f"FILTERING OUT TICKER: {ticker.ticker}")
            ticker_doc = client.collection(settings.Firestore.collection_ticker).document(doc.id)
            ticker_doc.set({
                u'status': 2
            }, merge=True)


def ticker_meaning(ticker: Ticker):
    dictionary = PyDictionary()
    return dictionary.meaning(ticker.ticker, disable_errors=True)


def get_tickers() -> list:
    """Return all active Tickers from the db.
    """
    client = firestore.Client()
    docs = client.collection(settings.Firestore.collection_ticker) \
        .where(u'status', u'>', 0) \
        .get()
    logging.info(f"(get_tickers) FIREBASE READ TICKER DOC COUNT: {len(docs)}")
    tickers = []
    for doc in docs:
        tickers.append(Ticker(doc.to_dict()))
    return list(set(tickers))


def check_for_ticker(text: str, tickers: [Ticker]) -> [Ticker]:
    """Search text for tickers from the passed Ticker list.
    Tickers with a status of 0 are ignored (should not be in passed list).
    Tickers with a status of 1 are searched for in all instances.
    Tickers with a status of 2 are searched for only combined with the "$" symbol.
    """
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


def ticker_px_update():
    """Update ticker prices in bulk - use the settings
    tickers (in one document) to avoid high read/write
    counts in firestore.
    """
    exchanges = ["nyse",
                 "nasdaq",
                 "amex",
                 # "euronex",
                 # "tsx",
                 # "index",
                 # "etf",
                 # "mutual_fund",
                 # "forex",
                 "crypto"]

    client = firestore.Client()
    # Get all pending casts to process while updating prices
    # 0=removed(system), 1=pending, 2=open(executed), 3=closed
    cast_docs = client.collection(settings.Firestore.collection_casts) \
        .where(u'status', u'==', 1) \
        .get()
    logging.info(f"(ticker_px_update) CASTS FOUND: {len(cast_docs)}")

    for exchange in exchanges:
        # print(f"trying exchange: {exchange}")
        try:
            response = requests.get("https://financialmodelingprep.com/api/v3/quotes/" +
                                    exchange +
                                    "?apikey=3460e3ef780cb0935bcb32471a210dba")
            response.raise_for_status()
            # print(f"exchange {exchange} response: {response.status_code}")
            # logging.info(f"(ticker_px_update) {exchange} TICKER COUNT: {len(response.json())}")

            exchange_tickers = []
            for t in response.json():
                t_data = {
                    'symbol': t['symbol'],
                    'name': t['name'],
                    'price': t['price'],
                    'volume': t['volume'],
                    'timestamp': t['timestamp'],
                }
                exchange_tickers.append(t_data)

                # Check whether the ticker is used in any active cast
                found_casts = filter(lambda x: x.to_dict()['ticker'] == t['symbol'], cast_docs)
                for cast in found_casts:
                    cast_data = cast.to_dict()
                    # print(f"found cast: {cast_data} while ticker price: {t['price']}")
                    new_cast_data = None
                    # found casts will be limit orders with status: 3=limit buy, 4=limit sell
                    # Limit Buy orders execute if the price has dropped AT OR BELOW the target price
                    if cast_data['type'] == 3 and t['price'] <= cast_data['price_target']:
                        new_cast_data = {
                            'status': 2,
                            'executed': time.time() * 1000,
                            'price_executed': t['price']
                        }

                    # Limit Sell orders execute if the price has risen AT OR ABOVE the target price
                    elif cast_data['type'] == 4 and t['price'] >= cast_data['price_target']:
                        new_cast_data = {
                            'status': 2,
                            'executed': time.time() * 1000,
                            'price_executed': t['price']
                        }

                    if new_cast_data is not None:
                        ticker_doc_ref = client.collection(settings.Firestore.collection_casts).document(cast.id)
                        ticker_doc_ref.set(new_cast_data, merge=True)

            # print(len(exchange_tickers))
            client.collection(settings.Firestore.collection_tickers)\
                .document(exchange)\
                .set({
                    'all': exchange_tickers,
                    'status': 1,
                })

        except HTTPError as http_err:
            # print(f'HTTP error occurred: {http_err}')
            logging.error(f"(ticker_px_update) HTTP ERROR: {http_err}")
            continue
        except Exception as err:
            # print(f'Other error occurred: {err}')
            logging.error(f"(ticker_px_update) UNKNOWN ERROR: {err}")
            continue


if __name__ == '__main__':
    # load_tickers('../data/tickers.csv')
    # logging.info(get_tickers())
    # filter_tickers()
    # fill_settings_tickers()
    # transform_tickers()

    import time
    while True:
        ticker_px_update()
        time.sleep(5)
