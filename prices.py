import time
import logging
import google.cloud.logging
from google.cloud.logging_v2.handlers import CloudLoggingHandler
from dotenv import load_dotenv

from anthracite import ticker
from reddit import reddit

debug = False
local = False


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

    while True:
        ticker.ticker_px_update()
        time.sleep(5)
