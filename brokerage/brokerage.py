import csv
import logging
import requests
from google.cloud import firestore
from utils import settings


# client = firestore.Client()
    # cast_docs = client.collection(settings.Firestore.collection_casts) \
    #     .where(u'status', u'==', 1) \
    #     .get()
    # logging.info(f"(ticker_px_update) CASTS FOUND: {len(cast_docs)}")
    # client.collection(settings.Firestore.collection_tickers) \
    #     .document(exchange) \
    #     .set({
    #     'all': exchange_tickers,
    #     'status': 1,
    # })


def robinhood():
    try:
        response = requests.get("https://api.robinhood.com/oauth2/token/")
        if response.status_code == 200:
            print(response)

        else:
            print(f"ERROR: {response}")

    except Exception:
        logging.error(f"(ticker_px_update) ERROR: {Exception}")


if __name__ == '__main__':
    robinhood()
