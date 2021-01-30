import logging
from google.cloud import firestore
from google.cloud import language_v1

from utils import settings


class Sentiment:
    def __init__(self,
                 sentiment: float,
                 magnitude: float,
                 ):
        self.sentiment = sentiment
        self.magnitude = magnitude


def all_sentiment_analysis() -> None:
    # Get the Notions without language analysis
    firestore_client = firestore.Client()
    language_client = language_v1.LanguageServiceClient()

    # Use magnitude to find the Notions not analyzed
    # since it is highly likely to be 0, while sentiment
    # might be 0 for many Notions.
    docs = firestore_client.collection(settings.Firestore.collection_notion) \
        .where(u'magnitude', u'==', 0) \
        .get()
    logging.info(f"(all_sentiment_analysis) FIREBASE READ NOTION DOC COUNT: {len(docs)}")
    for doc in docs:
        notion_dict = doc.to_dict()
        document = language_v1.Document(content=notion_dict['text'], type_=language_v1.Document.Type.PLAIN_TEXT)
        sentiment = language_client.analyze_sentiment(request={'document': document}).document_sentiment
        # print("Text: {}".format(s_text))
        # print("Sentiment: {}, {}".format(sentiment.score, sentiment.magnitude))

        notion_doc = firestore_client.collection(settings.Firestore.collection_notion).document(doc.id)
        notion_doc.set({
            'sentiment': sentiment.score,
            'magnitude': sentiment.magnitude,
        }, merge=True)


def sentiment_analysis(text: str) -> Sentiment:
    language_client = language_v1.LanguageServiceClient()
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    sentiment = language_client.analyze_sentiment(request={'document': document}).document_sentiment
    return Sentiment(sentiment=sentiment.score, magnitude=sentiment.magnitude)


if __name__ == '__main__':
    all_sentiment_analysis()
