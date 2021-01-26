from google.cloud import firestore
from google.cloud import language_v1

from utils import settings


def sentiment_analysis():
    # Get the Notions without language analysis
    firestore_client = firestore.Client()
    language_client = language_v1.LanguageServiceClient()

    # Use magnitude to find the Notions not analyzed
    # since it is highly likely to be 0, while sentiment
    # might be 0 for many Notions.
    docs = firestore_client.collection(settings.Firestore.collection_notion) \
        .where(u'magnitude', u'==', 0) \
        .get()
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


if __name__ == '__main__':
    sentiment_analysis()
