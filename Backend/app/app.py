from flask import jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
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


    @app.route("/auth/login", methods=["POST"])
    def login():
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid credentials"}), 401

        # Create JWT
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(days=1)
        )

        return jsonify({
            "access_token": access_token
        }), 200
    
    @app.route("/transactions", methods=["POST"])
    @jwt_required()
    def create_transaction():
        data = request.get_json()

        amount = data.get("amount")
        category = data.get("category")
        tx_type = data.get("type")

        if not amount or not category or tx_type not in ["income", "expense"]:
            return jsonify({"error": "Invalid transaction data"}), 400

        user_id = get_jwt_identity()

        transaction = Transaction(
            amount=amount,
            category=category,
            type=tx_type,
            user_id=user_id
        )

        db.session.add(transaction)
        db.session.commit()

        return jsonify({"message": "Transaction created"}), 201
