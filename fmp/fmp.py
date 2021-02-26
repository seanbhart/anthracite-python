import os
import logging
import requests

# from google.cloud import firestore


def quote_short(ticker: str):
    """Get the current price and volume for a ticker.
    """
    base_url = os.getenv("FMP_BASE_URL_QUOTE_SHORT")
    api_key = os.getenv("FMP_API")
    url = base_url + ticker + "?apikey=" + api_key

    r = requests.get(url)
    print(r.json())


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../local/.env")
    quote_short("AAPL")
