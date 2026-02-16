from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

import os

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        # Some providers expose postgres://, while SQLAlchemy expects postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            "sqlite:///" + os.path.join(BASE_DIR, "finance.db")
        )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
    }

    app.config["JWT_SECRET_KEY"] = os.getenv(
        "JWT_SECRET_KEY", "dev-secret-change-me"
    )

    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    CORS(
        app,
        resources={r"/*": {"origins": [frontend_origin]}},
        supports_credentials=False,
    )

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from . import models

    from .app import register_routes
    register_routes(app)

    return app
