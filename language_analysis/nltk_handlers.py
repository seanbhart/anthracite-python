from nltk.corpus import twitter_samples
from nltk.tag import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer


def lemmatize_sentence(tokens):
    lemmatizer = WordNetLemmatizer()
    lemmatized_sentence = []
    for word, tag in pos_tag(tokens):
        if tag.startswith('NN'):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'
        lemmatized_sentence.append(lemmatizer.lemmatize(word, pos))
    return lemmatized_sentence


def get_data():
    positive_tweets = twitter_samples.strings('/Users/seanhart/nltk_data/corpora/twitter_samples/positive_tweets.json')
    negative_tweets = twitter_samples.strings('/Users/seanhart/nltk_data/corpora/twitter_samples/negative_tweets.json')
    text = twitter_samples.strings('/Users/seanhart/nltk_data/corpora/twitter_samples/tweets.20150430-223406.json')
    tweet_tokens = twitter_samples.tokenized(
        '/Users/seanhart/nltk_data/corpora/twitter_samples/positive_tweets.json'
    )[0]
    print(tweet_tokens[0])
    print(lemmatize_sentence(tweet_tokens[0]))


if __name__ == '__main__':
    get_data()
