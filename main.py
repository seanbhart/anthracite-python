import os
import logging
import praw
from dotenv import load_dotenv
from google.cloud import language_v1

import reddit
from utils import tickers


def test():
    ticker_list = tickers.get_tickers()
    reddit_praw = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )
    subreddit = reddit_praw.subreddit("wallstreetbets")

    client = language_v1.LanguageServiceClient()
    # print(subreddit.display_name)  # output: redditdev
    # print(subreddit.title)  # output: reddit development
    # print(subreddit.description)  # output: a subreddit for discussion of ...
    for submission in subreddit.top("day"):
        # print(dir(submission))
        # pprint.pprint(vars(submission))
        # print(submission.title)
        s_text = submission.selftext
        if len(s_text) > 0:
            # Check whether a ticker is mentioned in the text
            for t in ticker_list:
                # Only use ticker with more than one letter and
                # add spaces before and after the ticker
                if len(t) > 1:
                    t_index = s_text.rfind(" " + t['ticker'] + " ")
                    t_index2 = s_text.rfind("$" + t['ticker'] + " ")
                    if t_index >= 0:
                        print("::"+s_text[t_index+1:t_index+len(t['ticker'])+1]+"::")
                        print("::"+s_text[t_index-10:t_index+10]+"::")
                    if t_index2 >= 0:
                        print("::"+s_text[t_index2+1:t_index2+len(t['ticker'])+1]+"::")
                        print("::"+s_text[t_index2-10:t_index2+10]+"::")
            document = language_v1.Document(content=s_text, type_=language_v1.Document.Type.PLAIN_TEXT)
            sentiment = client.analyze_sentiment(request={'document': document}).document_sentiment
            # print("Text: {}".format(s_text))
            print("Sentiment: {}, {}".format(sentiment.score, sentiment.magnitude))

        # all_comments = submission.comments.list()
        # for comment in all_comments:
        #     print(comment.body)


def main():
    print("START")
    # test()
    reddit.update()


debug = False
if __name__ == '__main__':
    load_dotenv(dotenv_path="./local/.env")
    logging.basicConfig(format='[%(asctime)s] {%(filename)s:%(lineno)d} - %(name)s - %(levelname)s - %(message)s')
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    main()
