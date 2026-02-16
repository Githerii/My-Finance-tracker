# Personal Finance Tracker

A full-stack app for tracking income, daily spending, and savings progress.

## What you can do
- Create an account and login securely (JWT auth).
- Add, view, update, and delete transactions.
- Filter transactions by type/category.
- Set a savings goal and monitor progress.
- See a summary of income, expenses, balance, and category spending.

## Tech Stack
- **Backend:** Flask, SQLAlchemy, Flask-Migrate, Flask-JWT-Extended
- **Frontend:** Next.js (TypeScript), Tailwind CSS
- **Database:** SQLite (default)

## Project Structure
- `Backend/` - Flask API
- `Frontend/` - Next.js UI

## Backend Setup
Run these commands from `Backend/` (not `Backend/app`):

```bash
cd Backend
pipenv install
pipenv shell
export FLASK_APP=app:create_app
flask db upgrade
flask run
```

Backend runs at `http://127.0.0.1:5000`.

If you already activated an older virtualenv before pulling changes, run:

```bash
pipenv --rm
pipenv install
pipenv shell
```


## Frontend Setup
From `Frontend/`:

```bash
npm install
cp .env.example .env.local
npm run dev
```

Frontend runs at `http://localhost:3000`.

## Environment Variables
### Backend
- `JWT_SECRET_KEY` (optional, defaults for local dev)
- `FRONTEND_ORIGIN` (optional, default `http://localhost:3000`)

### Frontend
- `NEXT_PUBLIC_API_URL` (default `http://127.0.0.1:5000`)

## API Endpoints
### Auth
- `POST /auth/register`
- `POST /auth/login`

### Transactions
- `POST /transactions`
- `GET /transactions`
- `PUT /transactions/<tx_id>`
- `DELETE /transactions/<tx_id>`

`GET /transactions` query params:
- `type=income|expense`
- `category=<string>`
- `start_date=YYYY-MM-DD`
- `end_date=YYYY-MM-DD`
- `limit=<int>`

### Savings + Summary
- `PATCH /me/savings-goal`
- `GET /me/summary`

## Notes
- Transaction amount must be a positive number.
- Transaction type must be `income` or `expense`.
- `occurred_on` date format is `YYYY-MM-DD`.
