from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.configuration.config import get_config

config = get_config()


INTERNAL_DATABASE_URL = f"mysql+mysqlconnector://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_INTERNAL}"
internal_engine = create_engine(INTERNAL_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=internal_engine)


Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
