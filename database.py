from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import sqlalchemy_utils


def get_engine():
    url = URL('postgresql+psycopg2', username='todo', password='todo', host='localhost',
              database='todo')
    engine = create_engine(url, echo=False)
    return engine


def create():
    from models import Base, TodoList, TodoListItem

    engine = get_engine()

    if sqlalchemy_utils.database_exists(engine.url):
        sqlalchemy_utils.drop_database(engine.url)
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


if __name__ == '__main__':
    create()
