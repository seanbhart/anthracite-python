from google.cloud import firestore

from utils import settings


class Ticker:
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
        client = firestore.Client()

        # If the Notion already exists, update existing data,
        # otherwise create a new Notion object.
        docs = client.collection(settings.Firestore.collection_notion) \
            .where(u'host', u'==', self.host) \
            .where(u'host_id', u'==', self.host_id) \
            .get()
        if len(docs) > 0:
            notion_doc_ref = client.collection(settings.Firestore.collection_notion).document(docs[0].id)
        else:
            notion_doc_ref = client.collection(settings.Firestore.collection_notion).document()
        # Remove all None values from the dict before uploading
        filtered = {k: v for k, v in self.__dict__.items() if v is not None}
        notion_doc_ref.set(filtered, merge=True)

        # # Update the tickers associated with the Notion to show new data was added
        # self.update_tickers()

    def update_tickers(self):
        client = firestore.Client()
        ticker_docs = client.collection(settings.Firestore.collection_ticker) \
            .where(u'ticker', u'in', self.tickers) \
            .get()

        # For each ticker in the Notion, update the ticker's latest timestamp
        # with the Notion's created time
        for td in ticker_docs:
            ticker_doc_ref = client.collection(settings.Firestore.collection_ticker).document(td.id)
            ticker_doc_ref.set({
                'latest_notion': self.created
            }, merge=True)
