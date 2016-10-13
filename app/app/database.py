from contextlib import contextmanager
import os
import time

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import sqlalchemy_utils

from app.models import *


def get_engine():
    username = os.environ['POSTGRES_USER']
    password = os.environ['POSTGRES_PASSWORD']
    database = os.environ['POSTGRES_DB']
    url = URL('postgresql+psycopg2', username=username, password=password, host='postgres', database=database)
    engine = create_engine(url, echo=False)
    return engine


def retry_db_exists(url, max_retries=5):
    timeout = 1
    retries = 0
    db_exsists = False

    while retries < max_retries:
        try:
            db_exsists = sqlalchemy_utils.database_exists(url)
            break
        except sqlalchemy.exc.OperationalError:
            time.sleep(timeout)
            timeout *= 2
            retries += 1
    if retries >= max_retries-1:
        raise RuntimeError('Could not connect to database')

    return db_exsists


def create(drop=False):
    engine = get_engine()

    retry_db_exists(engine.url)

    if sqlalchemy_utils.database_exists(engine.url):
        if drop:
            sqlalchemy_utils.drop_database(engine.url)
    else:
        sqlalchemy_utils.create_database(engine.url)
        Base.metadata.create_all(engine)


@contextmanager
def session_scope():
    engine = get_engine()
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

    session = Session()
    yield session
    try:
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
