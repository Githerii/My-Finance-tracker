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
- **Database:** SQLite (local), PostgreSQL (production)

## Project Structure
- `Backend/` - Flask API
- `Frontend/` - Next.js UI

## Local Development

### Backend setup
From `Backend/`:

```bash
pipenv install
pipenv shell
cp .env.example .env
export FLASK_APP=app:create_app
flask db upgrade
flask run
```

Backend runs at `http://127.0.0.1:5000`.

### Frontend setup
From `Frontend/`:

```bash
npm install
cp .env.example .env.local
npm run dev
```

Frontend runs at `http://localhost:3000`.

## Environment Variables

### Backend
- `DATABASE_URL` (optional; if not set, SQLite is used for local dev)
- `JWT_SECRET_KEY` (required for production)
- `FRONTEND_ORIGIN` (required for production, e.g. your Vercel domain)

### Frontend
- `NEXT_PUBLIC_API_URL` (required for deployment, points to backend API URL)

## Deployment Guide (Render + Vercel + iPhone)

### 1) Create a PostgreSQL database on Render
- In Render: **New** → **PostgreSQL**.
- Save the **Internal Database URL** (used by backend as `DATABASE_URL`).

### 2) Deploy backend on Render (Web Service)
Create a new web service from the repo and configure:

- **Root Directory:** `Backend`
- **Build Command:**
  ```bash
  pip install pipenv && pipenv install --system --deploy
  ```
- **Start Command:**
  ```bash
  gunicorn --bind 0.0.0.0:$PORT "app:create_app()"
  ```

Set backend environment variables in Render:
- `DATABASE_URL` = Render Postgres Internal Database URL
- `JWT_SECRET_KEY` = long random secret
- `FRONTEND_ORIGIN` = your Vercel app URL (e.g. `https://your-app.vercel.app`)

After the first successful deploy, run DB migrations in Render shell:

```bash
cd Backend
export FLASK_APP=app:create_app
flask db upgrade
```

> Repeat `flask db upgrade` each time you add new migrations.

### 3) Deploy frontend on Vercel
- Import the repo in Vercel.
- Set **Root Directory** to `Frontend`.
- Add env var:
  - `NEXT_PUBLIC_API_URL=https://<your-render-service>.onrender.com`
- Deploy.

### 4) Final CORS check
Ensure backend `FRONTEND_ORIGIN` exactly matches your Vercel domain (including `https://`).

### 5) Use on iPhone
- Open your Vercel URL in Safari.
- Optional: Share → **Add to Home Screen** for app-like access.

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
