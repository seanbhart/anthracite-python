from google.cloud import firestore

from utils import settings


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
            notion_doc = client.collection(settings.Firestore.collection_notion).document(docs[0].id)
        else:
            notion_doc = client.collection(settings.Firestore.collection_notion).document()
        notion_doc.set(self.__dict__, merge=True)
