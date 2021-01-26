import logging
from dotenv import load_dotenv

import reddit.model as rmodel
from reddit import reddit as red
from language_analysis.language_analysis import sentiment_analysis
from utils import tickers


def get_reddit_top_breadth(subreddit: str, recency: str, layers: int):
    print(f"GET SUBREDDIT {subreddit} TOP POSTS BY BREADTH IN LAST {recency}")
    ticker_list = tickers.get_tickers()
    notions = []
    i = 0
    for submission in red.get_top(subreddit=subreddit, recency=recency):
        notion = rmodel.notion_from_submission(submission.__dict__)
        found_tickers = tickers.check_for_ticker(notion.text, ticker_list)
        if found_tickers is not None:
            notion.tickers = list(map(lambda x: x.ticker, found_tickers))
            sentiment = sentiment_analysis(notion.text)
            notion.sentiment = sentiment.sentiment
            notion.magnitude = sentiment.magnitude
            notion.upload()
            notions.append(notion)

        # Reddit cannot serve too many comments
        if submission.num_comments > 90000:
            continue

        submission.comments.replace_more(limit=layers)
        for comment in submission.comments.list():
            notion2 = rmodel.notion_from_comment(comment.__dict__)
            found_tickers2 = tickers.check_for_ticker(notion2.text, ticker_list)
            if found_tickers2 is not None:
                notion2.tickers = list(map(lambda x: x.ticker, found_tickers2))
                sentiment = sentiment_analysis(notion2.text)
                notion2.sentiment = sentiment.sentiment
                notion2.magnitude = sentiment.magnitude
                notion2.upload()
                notions.append(notion2)
        i += 1
        if i > 1:
            break
    for n in notions:
        print(n.__dict__)


def process_notion(notion, ticker_list):
    found_tickers = tickers.check_for_ticker(notion.text, ticker_list)
    if found_tickers is None:
        return
    notion.tickers = list(map(lambda x: x.ticker, found_tickers))
    sentiment = sentiment_analysis(notion.text)
    notion.sentiment = sentiment.sentiment
    notion.magnitude = sentiment.magnitude
    # notion.upload()
    return notion


def get_reddit_top_depth(subreddit: str, recency: str, layers: int):
    print(f"GET SUBREDDIT {subreddit} TOP POSTS BY DEPTH IN LAST {recency}")
    ticker_list = tickers.get_tickers()
    notions = []
    i = 0
    for submission in red.get_top(subreddit=subreddit, recency=recency):
        notion = rmodel.notion_from_submission(submission.__dict__)
        # found_tickers = tickers.check_for_ticker(notion.text, ticker_list)
        # if found_tickers is not None:
        #     notion.tickers = list(map(lambda x: x.ticker, found_tickers))
        #     sentiment = sentiment_analysis(notion.text)
        #     notion.sentiment = sentiment.sentiment
        #     notion.magnitude = sentiment.magnitude
        #     notion.upload()
        notion_p = process_notion(notion, ticker_list)
        if notion_p:
            notions.append(notion_p)

        # Reddit cannot serve too many comments
        if submission.num_comments > 90000:
            continue

        submission.comments.replace_more(limit=layers)
        for comment in submission.comments:
            notion2 = rmodel.notion_from_comment(comment.__dict__)
            print(f"submission comment: {comment}")
            # notions.append(notion2)
            notion_p2 = process_notion(notion2, ticker_list)
            if notion_p2:
                notions.append(notion_p2)
            _, comment_notions = get_replies(comment, ticker_list)
            notions.extend(comment_notions)

        print(i)
        i += 1
        if i > 1:
            break
    for n in notions:
        print(n)


def get_replies(comment, ticker_list):
    print(f"get_replies comment: {comment}")
    comment_list = []
    notion_list = []
    for r1 in comment.replies:
        notion = rmodel.notion_from_comment(r1.__dict__)
        comment_list.append(r1)
        notion_p = process_notion(notion, ticker_list)
        if notion_p:
            notion_list.append(notion_p)
        reply_comments, reply_notions = get_replies(r1, ticker_list)
        print(f"get_replies reply: {r1}, reply replies: {reply_comments}")
        for r2 in reply_comments:
            print(r2)
            notion2 = rmodel.notion_from_comment(r2.__dict__)
            comment_list.append(r2)
            notion_p2 = process_notion(notion2, ticker_list)
            if notion_p2:
                notion_list.append(notion_p2)
    print(f"get_replies comment: {comment}, reply_list: {comment_list}")
    return comment_list, notion_list


def main():
    # get_reddit_top_breadth(subreddit="wallstreetbets", recency="day", layers=0)
    # get_reddit_top_breadth(subreddit="pennystocks", recency="day", layers=0)
    get_reddit_top_depth(subreddit="wallstreetbets", recency="hour", layers=2)


debug = False
if __name__ == '__main__':
    load_dotenv(dotenv_path="./local/.env")
    logging.basicConfig(format='[%(asctime)s] {%(filename)s:%(lineno)d} - %(name)s - %(levelname)s - %(message)s')
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    main()
