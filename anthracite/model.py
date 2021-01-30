import logging
from google.cloud import firestore

from db_local import db
from language_analysis.language_analysis import sentiment_analysis
from utils import settings


class Ticker:
    """A db object to retain settings regarding
    which and how to search for Ticker symbols in text.
    """
    def __init__(self,
                 ticker: str,
                 status: int,
                 name: str,
                 exchange: str,
                 ):
        self.ticker = ticker
        self.status = status
        self.name = name
        self.exchange = exchange

    def __init__(self, data: dict):
        self.ticker = data['ticker']
        self.status = data['status']
        self.name = data['name']
        self.exchange = data['exchange']


class Notion:
    """A db object mirroring key data components
    in a praw subreddit submission response. Also
    includes fields with default values for storing
    analysis values.
    """
    def __init__(self,
                 host: str,
                 host_id: str,
                 text: str,
                 created: float,
                 upvotes: int,
                 downvotes: int = 0,
                 award_count: int = 0,
                 response_count: int = 0,
                 media_link: str = None,
                 categories: [str] = [],
                 parent: str = None,
                 associated: [str] = [],
                 sentiment: float = 0.0,
                 magnitude: float = 0.0,
                 tickers: [str] = [],
                 confidence: float = 0.0,
                 db_id: str = None,
                 ):
        self.host = host
        self.host_id = host_id
        self.text = text
        self.created = created
        self.upvotes = upvotes
        self.downvotes = downvotes
        self.award_count = award_count
        self.response_count = response_count
        self.media_link = media_link
        self.categories = categories
        self.parent = parent
        self.associated = associated
        self.sentiment = sentiment
        self.magnitude = magnitude
        self.tickers = tickers
        self.confidence = confidence
        self.db_id = db_id

    def upload(self):
        """Upload a Notion to the db, but since it might already
        exist, query for the submission based on the stored id
        the host passed for this data. Use the local db to store
        a record of existing Notions - reduce read requests to Firestore.
        """
        # DO NOT update old data - this leads to unnecessary writes.
        if not db.reddit_submission_exists(self.host_id):
            # Store the submission in the local db first to prevent
            # another thread from uploading this submission while
            # it is still being processed (below).
            db.reddit_insert(self.host_id)

            # Run language analysis ONLY AFTER knowing this entry will be uploaded -
            # Google Natural Language analysis can get expensive.
            sentiment = sentiment_analysis(self.text)
            self.sentiment = sentiment.sentiment
            self.magnitude = sentiment.magnitude

            client = firestore.Client()
            notion_doc_ref = client.collection(settings.Firestore.collection_notion).document()

            # Remove all None values from the dict before uploading
            filtered = {k: v for k, v in self.__dict__.items() if v is not None}
            notion_doc_ref.set(filtered)  # , merge=True)

            # # Update the tickers associated with the Notion to show new data was added
            # NOTE: Jan 29, 2021: No need to update Ticker db objects for now - no client
            # is currently listening to Ticker objects for updates.
            # self.update_tickers()

    def update_tickers(self):
        """Update all Tickers found for this Notion to indicate new data
        has been added for this Ticker. This is useful if a client is
        listening for changes to Ticker documents.
        """
        client = firestore.Client()
        ticker_docs = client.collection(settings.Firestore.collection_ticker) \
            .where(u'ticker', u'in', self.tickers) \
            .get()
        logging.info(f"(update_tickers) FIREBASE READ TICKER DOC COUNT: {len(ticker_docs)}")

        # For each ticker in the Notion, update the ticker's latest timestamp
        # with the Notion's created time
        for td in ticker_docs:
            ticker_doc_ref = client.collection(settings.Firestore.collection_ticker).document(td.id)
            ticker_doc_ref.set({
                'latest_notion': self.created
            }, merge=True)
