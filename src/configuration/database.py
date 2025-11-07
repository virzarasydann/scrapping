from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.configuration.config import get_config

config = get_config()


INTERNAL_DATABASE_URL = f"mysql+mysqlconnector://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_INTERNAL}"
internal_engine = create_engine(INTERNAL_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=internal_engine)


CLIENT_DATABASE_URL = f"mysql+mysqlconnector://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_CLIENT}"
client_engine = create_engine(CLIENT_DATABASE_URL, pool_pre_ping=True)
ClientSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=client_engine)


Base = declarative_base()
ClientBase = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def get_db_client():
    db = ClientSessionLocal()
    try:
        yield db
    finally:
        db.close()
