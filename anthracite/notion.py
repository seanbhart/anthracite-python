from anthracite.ticker import check_for_ticker


def process_notion(notion, ticker_list):
    """Check a Notion object for Tickers and filter
    out any duplicates.

    UPDATE: DO NOT include sentiment analysis with Notion
    processing at this stage (at least for Google Natural
    Language). This is too expensive to process each Notion
    before determining whether it already exists in the database.
    """
    found_tickers = check_for_ticker(notion.text, ticker_list)
    if found_tickers is None:
        return
    notion.tickers = list(map(lambda x: x.ticker, found_tickers))
    return notion
