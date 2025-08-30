import os
from dotenv import load_dotenv

# load .env (akan membaca .env atau .env.prod tergantung APP_ENV)
load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")

class BaseConfig:
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "webhook_db")
    

class DevelopmentConfig(BaseConfig):
    DB_HOST = "103.191.92.250"   # host dev (bukan phpMyAdmin, tapi IP MySQL server)

class ProductionConfig(BaseConfig):
    DB_HOST = "localhost"

def get_config():
    if APP_ENV == "production":
        return ProductionConfig()
    return DevelopmentConfig()
