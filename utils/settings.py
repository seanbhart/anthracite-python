from google.cloud import firestore


class Firestore:
    """Settings for Firestore connections or
    data structures.
    """
    collection_casts = "casts"
    collection_host = "host"
    collection_notion = "notion"
    collection_ticker = "ticker"
    collection_tickers = "tickers"
    collection_settings = "settings"


def update_db_reddit() -> None:
    """Update reddit settings in the db.
    """
    client = firestore.Client()
    ticker_doc_ref = client.collection(Firestore.collection_host).document('reddit')
    ticker_doc_ref.set({
        'subreddits': [
            {'subreddit': "Wallstreetbets", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "Wallstreetbetsnew", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "StonkTraders", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "pennystocks", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "RobinHoodPennyStocks", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "Bitcoin", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "Bitcoincash", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "BitcoinMarkets", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "btc", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "ethereum", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "ethtrader", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "litecoin", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "LitecoinMarkets", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "dogecoin", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "SatoshiStreetBets", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "investing", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "RobinHood", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "options", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "StockMarket", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "finance", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "CryptoCurrency", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "economy", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "CryptoCurrencies", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "eos", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "Monero", 'recency': "hour", 'layers': 15, 'status': 1},
            {'subreddit': "Ripple", 'recency': "hour", 'layers': 15, 'status': 1},
        ]
    }, merge=True)


if __name__ == '__main__':
    update_db_reddit()
