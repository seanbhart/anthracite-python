import os
import logging
import praw
from statistics import mean

from reddit.model import notion_from_submission, notion_from_comment


def get_top(subreddit: str, recency: str):
    """The basic praw reddit top submission request.
    :returns: praw Iterator
    """
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )
    return reddit.subreddit(subreddit).top(recency)


def get_replies(comment, ticker_list) -> (list, list):
    """Recursively process all comments in a comment tree.
    Returns a tuple of two lists, a flattened comment list
    and a flattened processed Notion list.
    """
    comment_list = []
    notion_list = []
    for r1 in comment.replies:
        notion = notion_from_comment(r1.__dict__)
        comment_list.append(r1)
        notion_p = notion.process_notion(notion, ticker_list)
        if notion_p:
            notion_list.append(notion_p)
        reply_comments, reply_notions = get_replies(r1, ticker_list)
        for r2 in reply_comments:
            notion2 = notion_from_comment(r2.__dict__)
            comment_list.append(r2)
            notion_p2 = notion.process_notion(notion2, ticker_list)
            if notion_p2:
                notion_list.append(notion_p2)
    return comment_list, notion_list


def get_replies_with_sentiment(comment, ticker_list) -> (list, list, float, float):
    """Recursively process all comments in a comment tree,
    including sentiment analysis aggregation for the tree.
    Returns a tuple of two lists and two floats:
    - flattened comment list
    - flattened processed Notion list
    - weighted average sentiment float
    - weighted average magnitude float

    CAUTION: Sentiment analysis (Google Natural Language) is expensive,
    and this aggregation method should be used sparingly.
    """
    comment_list = []
    notion_list = []
    sentiment_all = []
    magnitude_all = []
    for r1 in comment.replies:
        sentiment_r1_all = []
        magnitude_r1_all = []
        reply_comments, _, _, _ = get_replies_with_sentiment(r1, ticker_list)
        for r2 in reply_comments:
            notion2 = notion_from_comment(r2.__dict__)
            comment_list.append(r2)
            notion_p2 = notion.process_notion(notion2, ticker_list)
            if notion_p2:
                notion_list.append(notion_p2)
                sentiment_r1_all.append(notion_p2.sentiment)
                magnitude_r1_all.append(notion_p2.magnitude)

        notion = notion_from_comment(r1.__dict__)
        comment_list.append(r1)
        notion_p = notion.process_notion(notion, ticker_list)
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
            logging.debug(f"NOTION: {notion_p.host_id}: S: {notion_p.sentiment}, M: {notion_p.magnitude} --- S: {sentiment_r1_final}, M: {magnitude_r1_final} --- TEXT: {notion_p.text}")

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
