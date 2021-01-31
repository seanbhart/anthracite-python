import logging
import google.cloud.logging
from google.cloud.logging_v2.handlers import CloudLoggingHandler
from dotenv import load_dotenv

from anthracite import ticker
from reddit import reddit

debug = False
local = False


def db_populate():
    from db_local import db
    db.reddit_populate()


def update_reddit_settings():
    from utils import settings
    settings.update_db_reddit()


def loop_reddit():
    # Update the ticker list when the loop is manually reset
    ticker_list = ticker.get_tickers()
    while True:
        logging.warning("REDDIT BREADTH START")
        reddit.process_reddit_breadth(ticker_list)


def main():
    if local:
        logging.warning("MAIN CALLED LOCAL")
    else:
        logging.warning("MAIN CALLED")
    loop_reddit()


if __name__ == '__main__':
    load_dotenv(dotenv_path="./local/.env")

    # The Google Cloud Logging module integrates with the Python
    # logging module to capture all logs thoughout the program.
    client = google.cloud.logging.Client()
    handler = CloudLoggingHandler(client)
    google.cloud.logging.handlers.setup_logging(handler)

    if debug:
        logging.basicConfig(format='[%(asctime)s] {%(filename)s:%(lineno)d} - %(name)s - %(levelname)s - %(message)s')
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        if local:
            logging.getLogger().setLevel(logging.INFO)
        else:
            logging.getLogger().setLevel(logging.WARNING)

    main()
    # update_reddit_settings()
