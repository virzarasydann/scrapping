# src/configuration/config.py
import json
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


SRC_DIR = Path(__file__).resolve().parent.parent
LOCAL_TEMP_DIR = SRC_DIR / "public" / "temp"

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
REMOTE_BASE_URL = os.environ["REMOTE_BASE_URL"]

GROUP_ID = os.getenv("GROUP_ID")


GREE_LOGIN_URL: str = os.environ["GREE_LOGIN_URL"]
GREE_HOME_URL: str = os.environ["GREE_HOME_URL"]


with open(f"{SRC_DIR}/cookies.json") as f:
    GREE_COOKIE_TEMP = json.load(f)

with open(f"{SRC_DIR}/elements.json") as f:
    LOCATORS = json.load(f)
   

class BaseConfig:
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_INTERNAL = os.getenv("DB_NAME", "webhook_db")
    DB_CLIENT = os.getenv("DB_CLIENT", "fs_track")


class DevelopmentConfig(BaseConfig):
    DB_HOST = "localhost"  


class ProductionConfig(BaseConfig):
    DB_HOST = os.environ["DB_HOST"]


def get_config():
    if APP_ENV == "production":
        return ProductionConfig()
    return DevelopmentConfig()
