

class Submission:
    def __init__(self,
                 reddit_id: str,
                 title: str,
                 text: str,
                 num_comments: int,
                 upvote_ratio: float,
                 ups: int,
                 total_awards_received: int,
                 created_utc: float,
                 media: str,
                 banned_by: str,
                 category: str,
                 parent: str = None
                 ):
        self.reddit_id = reddit_id
        self.title = title
        self.text = text
        self.num_comments = num_comments
        self.upvote_ratio = upvote_ratio
        self.ups = ups
        self.total_awards_received = total_awards_received
        self.created_utc = created_utc
        self.media = media
        self.banned_by = banned_by
        self.category = category
        self.parent = parent

    def from_dict(self, data: dict):
        self.reddit_id = data['reddit_id']
        self.title = data['title']
        self.text = data['text']
        self.num_comments = data['num_comments']
        self.upvote_ratio = data['upvote_ratio']
        self.ups = data['ups']
        self.total_awards_received = data['total_awards_received']
        self.created_utc = data['created_utc']
        self.media = data['media']
        self.banned_by = data['banned_by']
        self.category = data['category']
        self.parent = data['parent']
