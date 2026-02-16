from flask import Flask
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

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + os.path.join(BASE_DIR, "finance.db")
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["JWT_SECRET_KEY"] = os.getenv(
        "JWT_SECRET_KEY", "dev-secret-change-me"
    )

    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = frontend_origin
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        return response

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from . import models

    from .app import register_routes
    register_routes(app)

    return app
