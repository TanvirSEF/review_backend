# ReviewDibo API

This is the backend for **ReviewDibo**, a product review app. Users can browse products,
see average ratings, and write reviews. To post or edit a review, you need to log in. Only
admins can add products.

## Stack

- FastAPI — web framework
- PostgreSQL — database
- SQLAlchemy 2.0 — database toolkit
- Pydantic v2 — data validation
- bcrypt — password hashing
- PyJWT — login tokens

## How to run

You can run the app in two ways. Pick whichever you like.

### Option 1 — With Docker (easiest)

Docker runs everything for you — the database and the API together. You just need
[Docker](https://www.docker.com/) installed.

1. Copy the example settings file:

```powershell
Copy-Item .env.example .env
```

2. Add these three lines to your `.env` (they set up the database):

```ini
POSTGRES_USER=reviewdibo
POSTGRES_PASSWORD=change-me
POSTGRES_DB=reviewdibo
```

3. Start the app:

```powershell
docker compose up --build
```

Done. The API runs at http://localhost:8000. You don't need to set `DATABASE_URL` — Docker
connects it for you.

> The first run is a bit slow because Docker has to download and build the images.

### Option 2 — Without Docker (manual setup)

Use this if you already have PostgreSQL installed on your computer. You will need
Python 3.11+ and PostgreSQL 14+.

**Step 1 — Create a database**

The app builds its own tables, but the database has to exist first. Open `psql` and create
one (any name works — `reviewdibo` here):

```powershell
psql -U postgres -c "CREATE DATABASE reviewdibo;"
```

**Step 2 — Install the Python packages**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> If PowerShell says running scripts is disabled, run this once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
> (On macOS/Linux, activate with `source venv/bin/activate` instead.)

**Step 3 — Set up your `.env` file**

```powershell
Copy-Item .env.example .env
```

Then open `.env` and fill in two things:

- `DATABASE_URL` — the link to your database. It looks like this:
  `postgresql://USER:PASSWORD@localhost:5432/reviewdibo`
  Replace `USER` and `PASSWORD` with your own Postgres username and password.
- `JWT_SECRET` — a long random string. Make one with:
  `python -c "import secrets; print(secrets.token_hex(32))"`

**Step 4 — Run the app**

```powershell
fastapi dev app/main.py
```

The API runs at http://127.0.0.1:8000, and the docs are at http://127.0.0.1:8000/docs.

## Admin account

The app needs an admin to add products. On the first start, it creates an admin account
using `ADMIN_EMAIL` and `ADMIN_PASSWORD` from your `.env`. If you leave them empty, it uses
these defaults:

- Email: `admin@reviewdibo.com`
- Password: `admin`

This only happens once. Later restarts will not change it. **Tip:** set a strong
`ADMIN_PASSWORD` before the first run.

To use the admin, log in and copy the token it gives you:

```powershell
curl.exe -X POST localhost:8000/api/auth/login -d "username=admin@reviewdibo.com&password=<password>"
```

## Endpoints

**Open to everyone:**

- `POST /api/users` — register a new user
- `POST /api/auth/login` — log in and get a token
- `GET /api/products` — list products with their average ratings
- `GET /api/products/{id}` — see one product and its reviews

**Admin only:**

- `POST /api/products` — add a product

**Logged-in users:**

- `POST /api/reviews` — write a review
- `PUT /api/reviews/{id}` — edit your own review
- `DELETE /api/reviews/{id}` — delete your own review

You can also try all of these from the docs page at http://127.0.0.1:8000/docs using the
**Authorize** button.

## Environment variables

| Variable | Default | What it does |
| --- | --- | --- |
| `DATABASE_URL` | *(required)* | Link to your Postgres database. |
| `JWT_SECRET` | `change-me-in-production` | Secret key for login tokens. |
| `CORS_ORIGINS` | `*` | Allowed websites. Keep `*` only for local use. |
| `ADMIN_EMAIL` | `admin@reviewdibo.com` | The admin's email. |
| `ADMIN_PASSWORD` | `admin` | The admin's password. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | How long a login token lasts (minutes). |

## Project layout

```
app/
  main.py        starts the app, sets up routers and the database
  config.py      reads settings from your environment
  database.py    connects to the database
  security.py    passwords, login tokens, admin checks
  models/        User, Product, Review tables
  schemas/       what the data looks like in requests and responses
  routers/       auth, users, products, reviews
```
