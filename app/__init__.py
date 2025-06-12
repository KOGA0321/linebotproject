
# app/__init__.py

import os
import logging
from flask import Flask
from config import DevelopmentConfig, ProductionConfig

def create_app():
    app = Flask(__name__)

    # 環境に応じて設定を読み込む
    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # ── ロガー設定 ──
    # Flask 標準の logger と werkzeug のログレベルを設定
    app.logger.setLevel(app.config["LOG_LEVEL"])
    logging.getLogger("werkzeug").setLevel(app.config["LOG_LEVEL"])

    # ── Blueprint 登録 ──
    from .routes import bp as webhook_bp
    app.register_blueprint(webhook_bp)

    return app

