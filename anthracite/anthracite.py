

class Notion:
    def __init__(self,
                 db_id: str,
                 host: str,
                 text: str,
                 created: float,
                 upvotes: int,
                 upvote_ratio: float,
                 award_count: int = 0,
                 media_link: str = None,
                 category: str = None,
                 associated: [str] = [],
                 parent: str = None,
                 sentiment: float = 0.0,
                 magnitude: float = 0.0,
                 ticker: str = None,
                 confidence: float = 0.0,
                 ):
        self.db_id = db_id
        self.host = host
        self.text = text
        self.created = created
        self.upvotes = upvotes
        self.upvote_ratio = upvote_ratio
        self.award_count = award_count
        self.media_link = media_link
        self.category = category
        self.associated = associated
        self.parent = parent
        self.sentiment = sentiment
        self.magnitude = magnitude
        self.ticker = ticker
        self.confidence = confidence
