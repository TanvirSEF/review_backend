# ReviewDibo API

Backend for **ReviewDibo**, a product-review app. Users can browse products, see average
ratings, and write reviews — with JWT auth so only logged-in users can post or edit.
Products are managed by **admins**.

## Stack

FastAPI · PostgreSQL · SQLAlchemy 2.0 · Pydantic v2. Passwords are hashed with bcrypt and
auth tokens are JWT (PyJWT).

## Setup

### Prerequisites

- **Python 3.11+** — check with `python --version`.
- **PostgreSQL 14+** running locally. Install it natively, or skip to the
  [Docker](#with-docker) section and let compose spin one up for you.
- **Git Bash** on Windows (or any POSIX shell on macOS/Linux).

### 1. Install dependencies

```bash
python -m venv venv
source venv/Scripts/activate     # Windows · Git Bash
# source venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
```

### 2. Create the database

The app creates its own tables on startup, but the database itself has to exist first.
Any name works — `reviewdibo` here:

```bash
psql -U postgres -c "CREATE DATABASE reviewdibo;"
```

(Or `createdb reviewdibo`, or create it through pgAdmin / your DB tool.)

### 3. Configure your environment

```bash
cp .env.example .env
```

Open `.env` and fill in at least:

- **`DATABASE_URL`** — your Postgres connection string, in the form
  `postgresql://USER:PASSWORD@localhost:5432/reviewdibo`. Match the user, password, and
  database name you set up in Postgres.
- **JWT_SECRET** — a long random string. Generate one with
  `python -c "import secrets; print(secrets.token_hex(32))"`.

Optionally set **`ADMIN_EMAIL`** / **`ADMIN_PASSWORD`** now if you want the seeded admin to
use your own credentials instead of the defaults — see [Admin account](#admin-account).

### 4. Run

```bash
fastapi dev app/main.py
```

API on http://127.0.0.1:8000, interactive docs on http://127.0.0.1:8000/docs. Tables and
the admin account are created on first startup.

### With Docker

Prefer not to install Postgres by hand? `docker compose` brings up Postgres and the API
together. Add these three to your `.env` — compose uses them to create the database:

```ini
POSTGRES_USER=reviewdibo
POSTGRES_PASSWORD=change-me
POSTGRES_DB=reviewdibo
```

Then:

```bash
docker compose up --build
```

`DATABASE_URL` is wired for you (it points at the `db` service), so you don't set it here.
The API runs on http://localhost:8000.

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

## Admin account

Creating products is admin-only, so on startup the app makes sure an admin account exists.
Two quick things worth knowing — both are simple:

**Set the credentials in your environment.** The admin is built from two settings,
`ADMIN_EMAIL` and `ADMIN_PASSWORD`. Put the email and password you actually want into your
`.env` (locally) or your deploy platform's environment variables, and that's exactly what
the admin gets created with. Skip them and the app falls back to its built-in defaults:

| Setting | Default if you don't set it |
| --- | --- |
| `ADMIN_EMAIL` | `admin@reviewdibo.com` |
| `ADMIN_PASSWORD` | `admin` |

**It only runs once.** The seeder checks on every startup, but it only creates the admin
when one doesn't exist yet. So on the first start (a fresh database) the admin is created
with whatever you put in the env — and after that it's left untouched. Later restarts or
deploys won't recreate it, overwrite the password, or add a duplicate. (One side effect of
that: set a strong password *before* the first deploy. If you ever need to change it
afterwards, update it straight in the database.)

Once it exists, the admin logs in through the normal login endpoint to get a JWT, then
sends it as a `Bearer` token when creating products:

```bash
# log in as admin (copy access_token out of the response)
curl -X POST localhost:8000/api/auth/login \
  -d "username=admin@reviewdibo.com&password=<your-admin-password>"

# create a product with the admin token
curl -X POST localhost:8000/api/products \
  -H "Authorization: Bearer <paste-admin-token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Wireless Mouse","description":"Quiet clicks, USB-C.","image_url":"https://.../mouse.jpg"}'
```

> For production: the `admin` / `admin` defaults are just a convenience for local dev. Set a
> strong `ADMIN_PASSWORD` (and `ADMIN_EMAIL` if you like) in your environment before the
> first start.

## Endpoints

No login needed:

- `POST /api/users` — register
- `POST /api/auth/login` — log in, get a JWT
- `GET /api/products` — list, each with its average rating
- `GET /api/products/{id}` — one product and its reviews

Admin only (send `Authorization: Bearer <admin-token>`):

- `POST /api/products` — add a product

Login required (send `Authorization: Bearer <token>`):

- `POST /api/reviews` — write a review
- `PUT /api/reviews/{id}` — edit your own review
- `DELETE /api/reviews/{id}` — delete your own review

The author of a review is whoever is logged in, and you can only change your own reviews.
You can drive all of these from the **Authorize** button at http://127.0.0.1:8000/docs.

## Environment variables

| Variable | Default | Notes |
| --- | --- | --- |
| `DATABASE_URL` | — *(required)* | Postgres connection string. |
| `JWT_SECRET` | `change-me-in-production` | Set a long random string. |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins. Lock this down in prod. |
| `ADMIN_EMAIL` | `admin@reviewdibo.com` | Default admin email, seeded on startup. |
| `ADMIN_PASSWORD` | `admin` | Default admin password. Change in prod. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | JWT lifetime in minutes. |
