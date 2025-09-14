# src/configuration/config.py
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


SRC_DIR = Path(__file__).resolve().parent.parent


CONFIGURATION_DIR = Path(__file__).resolve().parent

PUBLIC_DIR = SRC_DIR / "public"

PUBLIC_DIR.mkdir(exist_ok=True)

TEMPLATES_DIR = SRC_DIR / "templates"


load_dotenv(ROOT_DIR / ".env", override=False)


APP_ENV = os.getenv("APP_ENV", "development")


if APP_ENV == "production":
    load_dotenv(ROOT_DIR / ".env.prod", override=True)
else:
    load_dotenv(ROOT_DIR / ".env", override=True)

TOKEN = os.getenv("TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
class BaseConfig:
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "webhook_db")

class DevelopmentConfig(BaseConfig):
    DB_HOST = "localhost"   # biasanya 127.0.0.1 juga bisa

class ProductionConfig(BaseConfig):
    DB_HOST = "localhost"

def get_config():
    if APP_ENV == "production":
        return ProductionConfig()
    return DevelopmentConfig()
