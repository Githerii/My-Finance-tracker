from flask import jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from datetime import timedelta

from .models import User
from . import db

def register_routes(app):

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "ok",
            "message": "Finance Tracker API running"
        })

    @app.route("/auth/register", methods=["POST"])
    def register():
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        # Basic validation
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Checks if user exists
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "User already exists"}), 409

        # Hashing the password
        password_hash = generate_password_hash(password)

        # Creates a user
        user = User(
            email=email,
            password_hash=password_hash
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201
