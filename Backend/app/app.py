from datetime import date, datetime, timedelta

from flask import jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .models import Transaction, User


def _parse_positive_amount(value):
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return None
    if amount <= 0:
        return None
    return round(amount, 2)


def _parse_iso_date(value):
    if value is None:
        return date.today()
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def register_routes(app):
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok", "message": "Finance Tracker API running"})

    @app.route("/auth/register", methods=["POST"])
    def register():
        data = request.get_json() or {}

        email = (data.get("email") or "").strip().lower()
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "User already exists"}), 409

        user = User(email=email, password_hash=generate_password_hash(password))

        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201

    @app.route("/auth/login", methods=["POST"])
    def login():
        data = request.get_json() or {}

        email = (data.get("email") or "").strip().lower()
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid credentials"}), 401

        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(days=1),
        )

        return jsonify({"access_token": access_token}), 200

    @app.route("/transactions", methods=["POST"])
    @jwt_required()
    def create_transaction():
        data = request.get_json() or {}

        amount = _parse_positive_amount(data.get("amount"))
        category = (data.get("category") or "").strip()
        tx_type = data.get("type")
        note = (data.get("note") or "").strip() or None
        occurred_on = _parse_iso_date(data.get("occurred_on"))

        if amount is None or not category or tx_type not in ["income", "expense"] or occurred_on is None:
            return (
                jsonify(
                    {
                        "error": "Invalid transaction data. Required: positive amount, category, type(income|expense), optional occurred_on(YYYY-MM-DD)",
                    }
                ),
                400,
            )

        user_id = int(get_jwt_identity())

        transaction = Transaction(
            amount=amount,
            category=category,
            type=tx_type,
            note=note,
            occurred_on=occurred_on,
            user_id=user_id,
        )

        db.session.add(transaction)
        db.session.commit()

        return jsonify({"message": "Transaction created", "transaction": transaction.to_dict()}), 201

    @app.route("/transactions", methods=["GET"])
    @jwt_required()
    def get_transactions():
        user_id = int(get_jwt_identity())

        tx_type = request.args.get("type")
        category = request.args.get("category")
        start_date = _parse_iso_date(request.args.get("start_date")) if request.args.get("start_date") else None
        end_date = _parse_iso_date(request.args.get("end_date")) if request.args.get("end_date") else None
        limit = request.args.get("limit", type=int)

        if tx_type and tx_type not in ["income", "expense"]:
            return jsonify({"error": "Invalid type filter"}), 400
        if request.args.get("start_date") and start_date is None:
            return jsonify({"error": "Invalid start_date, use YYYY-MM-DD"}), 400
        if request.args.get("end_date") and end_date is None:
            return jsonify({"error": "Invalid end_date, use YYYY-MM-DD"}), 400

        query = Transaction.query.filter_by(user_id=user_id)
        if tx_type:
            query = query.filter(Transaction.type == tx_type)
        if category:
            query = query.filter(Transaction.category == category)
        if start_date:
            query = query.filter(Transaction.occurred_on >= start_date)
        if end_date:
            query = query.filter(Transaction.occurred_on <= end_date)

        query = query.order_by(Transaction.occurred_on.desc(), Transaction.created_at.desc())
        if limit and limit > 0:
            query = query.limit(limit)

        return jsonify([tx.to_dict() for tx in query.all()]), 200

    @app.route("/transactions/<int:tx_id>", methods=["PUT"])
    @jwt_required()
    def update_transaction(tx_id):
        user_id = int(get_jwt_identity())
        transaction = Transaction.query.filter_by(id=tx_id, user_id=user_id).first()

        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404

        data = request.get_json() or {}

        if "amount" in data:
            amount = _parse_positive_amount(data.get("amount"))
            if amount is None:
                return jsonify({"error": "Amount must be a positive number"}), 400
            transaction.amount = amount

        if "category" in data:
            category = (data.get("category") or "").strip()
            if not category:
                return jsonify({"error": "Category cannot be empty"}), 400
            transaction.category = category

        if "type" in data:
            if data.get("type") not in ["income", "expense"]:
                return jsonify({"error": "Type must be income or expense"}), 400
            transaction.type = data.get("type")

        if "note" in data:
            transaction.note = (data.get("note") or "").strip() or None

        if "occurred_on" in data:
            occurred_on = _parse_iso_date(data.get("occurred_on"))
            if occurred_on is None:
                return jsonify({"error": "occurred_on must be YYYY-MM-DD"}), 400
            transaction.occurred_on = occurred_on

        db.session.commit()

        return jsonify({"message": "Transaction updated", "transaction": transaction.to_dict()}), 200

    @app.route("/transactions/<int:tx_id>", methods=["DELETE"])
    @jwt_required()
    def delete_transaction(tx_id):
        user_id = int(get_jwt_identity())

        transaction = Transaction.query.filter_by(id=tx_id, user_id=user_id).first()

        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404

        db.session.delete(transaction)
        db.session.commit()

        return jsonify({"message": "Transaction deleted"}), 200

    @app.route("/me/savings-goal", methods=["PATCH"])
    @jwt_required()
    def update_savings_goal():
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.get_json() or {}
        goal = _parse_positive_amount(data.get("savings_goal"))
        if goal is None:
            return jsonify({"error": "savings_goal must be a positive number"}), 400

        user.savings_goal = goal
        db.session.commit()

        return jsonify({"message": "Savings goal updated", "savings_goal": user.savings_goal}), 200

    @app.route("/me/summary", methods=["GET"])
    @jwt_required()
    def get_summary():
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        transactions = Transaction.query.filter_by(user_id=user_id).all()

        total_income = round(sum(tx.amount for tx in transactions if tx.type == "income"), 2)
        total_expense = round(sum(tx.amount for tx in transactions if tx.type == "expense"), 2)
        balance = round(total_income - total_expense, 2)

        expenses_by_category = {}
        for tx in transactions:
            if tx.type == "expense":
                expenses_by_category[tx.category] = round(
                    expenses_by_category.get(tx.category, 0) + tx.amount, 2
                )

        savings_goal = round(user.savings_goal or 0, 2)
        savings_progress = max(balance, 0)
        remaining_to_goal = round(max(savings_goal - savings_progress, 0), 2)

        return (
            jsonify(
                {
                    "total_income": total_income,
                    "total_expense": total_expense,
                    "balance": balance,
                    "savings_goal": savings_goal,
                    "savings_progress": round(savings_progress, 2),
                    "remaining_to_goal": remaining_to_goal,
                    "transaction_count": len(transactions),
                    "expenses_by_category": expenses_by_category,
                }
            ),
            200,
        )
