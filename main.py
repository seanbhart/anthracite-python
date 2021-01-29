import logging
from dotenv import load_dotenv

from reddit import reddit as red


subreddits = [
    {'subreddit': "Wallstreetbets", 'recency': "hour", 'layers': 10},
    {'subreddit': "Wallstreetbetsnew", 'recency': "hour", 'layers': 10},
    {'subreddit': "StonkTraders", 'recency': "hour", 'layers': 10},
    {'subreddit': "pennystocks", 'recency': "hour", 'layers': 10},
    {'subreddit': "RobinHoodPennyStocks", 'recency': "hour", 'layers': 10},
    {'subreddit': "Bitcoin", 'recency': "hour", 'layers': 10},
    {'subreddit': "Bitcoincash", 'recency': "hour", 'layers': 10},
    {'subreddit': "BitcoinMarkets", 'recency': "hour", 'layers': 10},
    {'subreddit': "btc", 'recency': "hour", 'layers': 10},
    {'subreddit': "ethereum", 'recency': "hour", 'layers': 10},
    {'subreddit': "ethtrader", 'recency': "hour", 'layers': 10},
    {'subreddit': "litecoin", 'recency': "hour", 'layers': 10},
    {'subreddit': "LitecoinMarkets", 'recency': "hour", 'layers': 10},
    {'subreddit': "dogecoin", 'recency': "hour", 'layers': 10},
    {'subreddit': "SatoshiStreetBets", 'recency': "hour", 'layers': 10},
]


def main():
    while True:
        for subreddit in subreddits:
            red.get_reddit_top_breadth(subreddit=subreddit['subreddit'],
                                       recency=subreddit['recency'],
                                       layers=subreddit['layers']
                                       )


debug = False
if __name__ == '__main__':
    load_dotenv(dotenv_path="./local/.env")
    logging.basicConfig(format='[%(asctime)s] {%(filename)s:%(lineno)d} - %(name)s - %(levelname)s - %(message)s')
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
    main()
