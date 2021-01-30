import logging
from dotenv import load_dotenv

from reddit import reddit


def main():
    reddit.process_reddit_breadth()


debug = False
if __name__ == '__main__':
    load_dotenv(dotenv_path="./local/.env")
    logging.basicConfig(format='[%(asctime)s] {%(filename)s:%(lineno)d} - %(name)s - %(levelname)s - %(message)s')
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.WARNING)
    main()
