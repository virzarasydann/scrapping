# src/configuration/config.py
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ambil APP_ENV dari environment OS dulu
APP_ENV = os.getenv("APP_ENV", "development")

# pilih file env sesuai APP_ENV
if APP_ENV == "production":
    env_file = BASE_DIR / ".env.prod"
else:
    env_file = BASE_DIR / ".env"

# load file env yang sesuai
load_dotenv(env_file)

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
