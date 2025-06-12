# config.py

import os
import logging


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-fallback")
    # 共通設定
    CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
    CHANNEL_SECRET       = os.getenv("CHANNEL_SECRET")
    OPENAI_API_KEY       = os.getenv("OPENAI_API_KEY")

    LOG_LEVEL = logging.INFO


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV   = "development"

    LOG_LEVEL = logging.DEBUG

    # 開発用 DB 等があればここに
    SQLALCHEMY_DATABASE_URI = "sqlite:///dev_chatlog.db"


class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV   = "production"
    LOG_LEVEL = logging.WARNING
    # 本番用 DB URI
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///prod_chatlog.db")

