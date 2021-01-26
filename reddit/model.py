from anthracite import model


def notion_from_submission(data: dict) -> model.Notion:
    """Create a Notion object from a Reddit Submission object.
    Returns Notion object or None if filtered out.
    """
    # Ensure the submission has not been banned
    if 'banned_by' in data and data['banned_by'] is not None:
        return None

    text = data['title']
    if 'text' in data:
        text = data['title'] + "\n\n" + data['text']

    return model.Notion(host="reddit",
                        host_id=data['id'],
                        text=text,
                        created=data['created_utc'],
                        upvotes=data['ups'],
                        downvotes=data['downs'],
                        award_count=data['total_awards_received'],
                        response_count=data['num_comments'],
                        media_link=data['media'],
                        categories=[data['category'], data['subreddit_name_prefixed']],
                        )


def notion_from_comment(data: dict) -> model.Notion:
    """Create a Notion object from a Reddit Comment object.
    Returns Notion object or None if filtered out.
    """
    # Ensure the submission has not been banned
    if 'banned_by' in data and data['banned_by'] is not None:
        return None

    return model.Notion(host="reddit",
                        host_id=data['id'],
                        text=data['body'],
                        created=data['created_utc'],
                        upvotes=data['ups'],
                        downvotes=data['downs'],
                        award_count=data['total_awards_received'],
                        parent=data['parent_id'],
                        associated=[data['parent_id']],
                        categories=[data['subreddit_name_prefixed']],
                        )
