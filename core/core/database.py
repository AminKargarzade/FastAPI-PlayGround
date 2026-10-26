from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import make_url

from core.config import settings

database_url = make_url(settings.SQLALCHEMY_DATABASE_URL)

if database_url.get_backend_name() == "sqlite" and database_url.database:
    db_path = Path(database_url.database)

    if not db_path.is_absolute():
        db_path = (Path(__file__).resolve().parents[1] / db_path).resolve()

    database_url = database_url.set(database=str(db_path))

engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
