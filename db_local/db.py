import os
import logging
import psycopg2

from google.cloud import firestore
from utils import settings


def reddit_insert(submission_host_id: str):
    """Insert a new reddit submission id into the local
    database. A timestamp of the time of insertion will
    be included. Existing data will not be overridden.
    Call the submission id lookup function first to determine
    if the submission already exists.
    """
    conn = psycopg2.connect(
        dbname=os.getenv("PSQL_DB"),
        user=os.getenv("PSQL_USER"),
        password=os.getenv("PSQL_PW"),
    )
    sql = """
        INSERT INTO reddit(id)
        VALUES (%s)
        ON CONFLICT DO NOTHING
    """
    try:
        cur = conn.cursor()
        cur.execute(sql, (submission_host_id,))
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"POSTGRES INSERT ERROR: {error}")
    finally:
        if conn is not None:
            conn.close()


def reddit_submission_exists(submission_host_id: str) -> bool:
    """Query the local reddit db to determine if a submission
    has already been added. If the submission exists locally,
    it should also exist in the primary remote db. Returns
    a boolean indicator whether the Notion already exists.
    """
    exists = False
    conn = psycopg2.connect(
        dbname=os.getenv("PSQL_DB"),
        user=os.getenv("PSQL_USER"),
        password=os.getenv("PSQL_PW"),
    )
    sql = """
        SELECT id FROM reddit
        WHERE id=%s
    """
    try:
        cur = conn.cursor()
        cur.execute(sql, (submission_host_id,))
        if len(cur.fetchall()) > 0:
            exists = True
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"POSTGRES INSERT ERROR: {error}")
    finally:
        if conn is not None:
            conn.close()
        return exists


def reddit_populate():
    """A standalone function to get all existing Notions
    from the remote db from reddit and insert them into
    the local database for initial population.
    """
    # Get existing Notions from Firestore.
    client = firestore.Client()
    docs = client.collection(settings.Firestore.collection_notion) \
        .where(u'host', u'==', 'reddit').limit(2000) \
        .get()
    # Extract just the host's data id an add to a list
    ids = []
    for doc in docs:
        doc_dict = doc.to_dict()
        ids.append(doc_dict['host_id'])

    # Add all to the local db.
    conn = psycopg2.connect(
        dbname=os.getenv("PSQL_DB"),
        user=os.getenv("PSQL_USER"),
        password=os.getenv("PSQL_PW"),
    )
    try:
        cur = conn.cursor()
        # args_str = ','.join(cur.mogrify("(%s)", i) for i in ids)
        # cur.execute("INSERT INTO reddit VALUES " + args_str)
        cur.executemany("INSERT INTO reddit(id) VALUES(%s) ON CONFLICT DO NOTHING", [[i] for i in ids])
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"POSTGRES INSERT ERROR: {error}")
    finally:
        if conn is not None:
            conn.close()
