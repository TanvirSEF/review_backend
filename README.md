# ReviewDibo API

Product-review backend. Users browse products, read average ratings, and post reviews; JWT
auth gates posting and editing. Products are admin-managed.

## Stack

FastAPI · PostgreSQL · SQLAlchemy 2.0 · Pydantic v2 · bcrypt · PyJWT.

## Setup

**Prerequisites:** Python 3.11+, PostgreSQL 14+ (or use [Docker](#docker)).

```powershell
python -m venv venv
venv\Scripts\Activate.ps1            # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create the database (the app creates the tables itself on startup):

```powershell
psql -U postgres -c "CREATE DATABASE reviewdibo;"
```

Configure and run:

```powershell
Copy-Item .env.example .env          # then edit DATABASE_URL and JWT_SECRET
fastapi dev app/main.py
```

- `DATABASE_URL` — `postgresql://USER:PASSWORD@localhost:5432/reviewdibo`
- `JWT_SECRET` — generate with `python -c "import secrets; print(secrets.token_hex(32))"`

API at http://127.0.0.1:8000 · docs at http://127.0.0.1:8000/docs.

> PowerShell blocking activation? Run
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

### Docker

Add to `.env`, then `docker compose up --build`:

```ini
POSTGRES_USER=reviewdibo
POSTGRES_PASSWORD=change-me
POSTGRES_DB=reviewdibo
```

`DATABASE_URL` is wired to the `db` service automatically. API on http://localhost:8000.

## Admin account

An admin is seeded on first startup from `ADMIN_EMAIL` / `ADMIN_PASSWORD` (defaults:
`admin@reviewdibo.com` / `admin`). It runs once — later restarts never overwrite it, so
**set a strong `ADMIN_PASSWORD` before the first start.** Log in normally, then call admin
endpoints with the returned Bearer token:

```powershell
curl.exe -X POST localhost:8000/api/auth/login -d "username=admin@reviewdibo.com&password=<pwd>"
```

## Endpoints

| Endpoint | Auth | Description |
| --- | --- | --- |
| `POST /api/users` | – | register |
| `POST /api/auth/login` | – | login, returns JWT |
| `GET /api/products` | – | list with average rating + review count |
| `GET /api/products/{id}` | – | product with its reviews |
| `POST /api/products` | admin | create product |
| `POST /api/reviews` | user | create review |
| `PUT /api/reviews/{id}` | user | edit own review |
| `DELETE /api/reviews/{id}` | user | delete own review |

## Environment variables

| Variable | Default | Notes |
| --- | --- | --- |
| `DATABASE_URL` | — *(required)* | Postgres connection string. |
| `JWT_SECRET` | `change-me-in-production` | Long random string. |
| `CORS_ORIGINS` | `*` | Comma-separated origins. Lock down in prod. |
| `ADMIN_EMAIL` | `admin@reviewdibo.com` | Seeded admin email. |
| `ADMIN_PASSWORD` | `admin` | Seeded admin password. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | JWT lifetime in minutes. |

## Layout

```
app/
  main.py        app + router wiring + startup (schema check + admin seed)
  config.py      settings from env
  database.py    engine + session + lightweight column migration
  security.py    hashing, JWT, current user, admin guard, admin seeding
  models/        User, Product, Review
  schemas/       Pydantic schemas
  routers/       auth, users, products, reviews
```
