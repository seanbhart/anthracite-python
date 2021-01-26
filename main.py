import logging
from dotenv import load_dotenv
from statistics import mean

from anthracite import anthracite
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


# def process_notion(notion, ticker_list):
#     found_tickers = tickers.check_for_ticker(notion.text, ticker_list)
#     if found_tickers is None:
#         return
#     notion.tickers = list(map(lambda x: x.ticker, found_tickers))
#     sentiment = sentiment_analysis(notion.text)
#     notion.sentiment = sentiment.sentiment
#     notion.magnitude = sentiment.magnitude
#     # notion.upload()
#     return notion


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
        notion_p = anthracite.process_notion(notion, ticker_list)
        if notion_p:
            notions.append(notion_p)

        # Reddit cannot serve too many comments
        if submission.num_comments > 90000:
            continue

        sentiment_all = []
        magnitude_all = []
        submission.comments.replace_more(limit=layers)
        for comment in submission.comments:
            notion2 = rmodel.notion_from_comment(comment.__dict__)
            # print(f"submission comment: {comment}")
            notion_p2 = anthracite.process_notion(notion2, ticker_list)
            if notion_p2:
                notions.append(notion_p2)
            _, comment_notions, sentiment_c, magnitude_c = get_replies_with_sentiment(comment, ticker_list)
            notions.extend(comment_notions)
            if sentiment_c:
                sentiment_all.append(sentiment_c)
            if magnitude_c:
                magnitude_all.append(magnitude_c)

        if notion_p and len(sentiment_all) > 1 and len(magnitude_all) > 1:
            sentiment_adj = mean([notion_p.sentiment, mean(sentiment_all)])
            magnitude_adj = mean([notion_p.magnitude, mean(magnitude_all)])
            print(f"NOTION: {notion_p.host_id}: S: {notion_p.sentiment}, M: {notion_p.magnitude} --- S: {sentiment_adj}, M: {magnitude_adj} --- TEXT: {notion_p.text}")
        print(i)
        i += 1
        # if i > 5:
        #     break
    # for n in notions:
    #     print(n)


def get_replies_with_sentiment(comment, ticker_list):
    comment_list = []
    notion_list = []
    sentiment_all = []
    magnitude_all = []
    for r1 in comment.replies:
        sentiment_r1_all = []
        magnitude_r1_all = []
        reply_comments, _, _, _ = get_replies_with_sentiment(r1, ticker_list)
        for r2 in reply_comments:
            notion2 = rmodel.notion_from_comment(r2.__dict__)
            comment_list.append(r2)
            notion_p2 = anthracite.process_notion(notion2, ticker_list)
            if notion_p2:
                notion_list.append(notion_p2)
                sentiment_r1_all.append(notion_p2.sentiment)
                magnitude_r1_all.append(notion_p2.magnitude)

        notion = rmodel.notion_from_comment(r1.__dict__)
        comment_list.append(r1)
        notion_p = anthracite.process_notion(notion, ticker_list)
        if notion_p:
            notion_list.append(notion_p)
            sentiment_r1_final = notion_p.sentiment
            if len(sentiment_r1_all) == 1:
                sentiment_r1_final = mean([notion_p.sentiment, sentiment_r1_all[0]])
            elif len(sentiment_r1_all) > 1:
                sentiment_r1_final = mean([notion_p.sentiment, mean(sentiment_r1_all)])
            sentiment_all.append(sentiment_r1_final)
            magnitude_r1_final = notion_p.magnitude
            if len(magnitude_r1_all) == 1:
                magnitude_r1_final = mean([notion_p.magnitude, magnitude_r1_all[0]])
            elif len(magnitude_r1_all) > 1:
                magnitude_r1_final = mean([notion_p.magnitude, mean(magnitude_r1_all)])
            magnitude_all.append(magnitude_r1_final)
            print(f"NOTION: {notion_p.host_id}: S: {notion_p.sentiment}, M: {notion_p.magnitude} --- S: {sentiment_r1_final}, M: {magnitude_r1_final} --- TEXT: {notion_p.text}")

    sentiment_all_final = None
    if len(sentiment_all) == 1:
        sentiment_all_final = sentiment_all[0]
    elif len(sentiment_all) > 1:
        sentiment_all_final = mean(sentiment_all)
    magnitude_all_final = None
    if len(magnitude_all) == 1:
        magnitude_all_final = magnitude_all[0]
    elif len(magnitude_all) > 1:
        magnitude_all_final = mean(magnitude_all)
    return comment_list, notion_list, sentiment_all_final, magnitude_all_final


def main():
    # get_reddit_top_breadth(subreddit="wallstreetbets", recency="hour", layers=0)
    # get_reddit_top_breadth(subreddit="pennystocks", recency="hour", layers=0)
    get_reddit_top_depth(subreddit="wallstreetbets", recency="hour", layers=3)


debug = False
if __name__ == '__main__':
    load_dotenv(dotenv_path="./local/.env")
    logging.basicConfig(format='[%(asctime)s] {%(filename)s:%(lineno)d} - %(name)s - %(levelname)s - %(message)s')
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    main()
