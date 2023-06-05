import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import dotenv

dotenv.load_dotenv(".env")

engine = create_engine(
    f"mysql+pymysql://{os.getenv('MYSQL_USER_NAME')}:{os.getenv('MYSQL_USER_PASSWORD')}@db:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}",
    echo=True,
)

DBSession = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = DBSession.query_property()


@contextmanager
def session_maker_modify(session=DBSession):
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise ValueError("Create session failed. Already rollback the database")
    finally:
        session.close()


@contextmanager
def session_maker_readonly(session=DBSession):
    try:
        yield session
    except:
        session.rollback()
        raise ValueError("Create session failed. Already rollback the database")
    finally:
        session.close()


def init_db():
    from pathlib import Path
    import sys

    sys.path.append(Path(__file__).resolve().parent.parent.__str__())
    import api.models

    Base.metadata.create_all(bind=engine)
