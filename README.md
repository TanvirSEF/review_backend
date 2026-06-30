# ReviewDibo API

Backend for **ReviewDibo**, a product review app. Users can browse products, see average
ratings, and write reviews. To post or edit a review you need to log in, and only admins
can add products.

## Stack

FastAPI, PostgreSQL, SQLAlchemy 2.0, Pydantic v2, bcrypt (password hashing), PyJWT (login
tokens).

## How to run

There are two ways. Docker is the easier one.

### With Docker (easier)

Make sure [Docker](https://www.docker.com/) is installed, then:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

That's it. The database and the API start together, and the API runs at
http://localhost:8000.

The `POSTGRES_*` values in `.env` are already filled in for you. Change the password if you
want something stronger. You don't need to touch `DATABASE_URL` — Docker wires it up.

> The first run is slow because Docker has to download the images.

### Without Docker (your own Postgres)

You'll need Python 3.11+ and PostgreSQL 14+ on your machine.

First, create the database (the app builds its own tables, but the database must exist
first):

```powershell
psql -U postgres -c "CREATE DATABASE reviewdibo;"
```

Set up a virtual environment and install the packages:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy the settings file:

```powershell
Copy-Item .env.example .env
```

Open `.env` and fill in two values:

- `DATABASE_URL` — your database link. Replace the username and password with your Postgres
  ones: `postgresql://USER:PASSWORD@localhost:5432/reviewdibo`
- `JWT_SECRET` — a random string. Make one with
  `python -c "import secrets; print(secrets.token_hex(32))"`

Now run it:

```powershell
fastapi dev app/main.py
```

API at http://127.0.0.1:8000, docs at http://127.0.0.1:8000/docs.

> If PowerShell blocks the activation script, run this once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
> (On macOS/Linux, use `source venv/bin/activate` instead.)

## Admin account

The app needs an admin to add products. On the first start it creates one from
`ADMIN_EMAIL` and `ADMIN_PASSWORD` in your `.env`. If you leave them, it uses these:

- Email: `admin@reviewdibo.com`
- Password: `admin`

This only happens once — later restarts won't change it. Set a strong `ADMIN_PASSWORD`
before the first run.

To use the admin, log in and grab the token:

```powershell
curl.exe -X POST localhost:8000/api/auth/login -d "username=admin@reviewdibo.com&password=<password>"
```

## Endpoints

**Open to everyone**

- `POST /api/users` — register
- `POST /api/auth/login` — log in, get a token
- `GET /api/products` — list products with average ratings
- `GET /api/products/{id}` — one product with its reviews

**Admin only**

- `POST /api/products` — add a product

**Logged-in users**

- `POST /api/reviews` — write a review
- `PUT /api/reviews/{id}` — edit your own review
- `DELETE /api/reviews/{id}` — delete your own review

You can also drive all of these from the docs page at http://127.0.0.1:8000/docs using the
**Authorize** button.

## Environment variables

| Variable | Default | What it does |
| --- | --- | --- |
| `DATABASE_URL` | *(required)* | Link to your Postgres database. |
| `JWT_SECRET` | `change-me-in-production` | Secret key for login tokens. |
| `CORS_ORIGINS` | `*` | Allowed websites. `*` is fine for local only. |
| `ADMIN_EMAIL` | `admin@reviewdibo.com` | The admin's email. |
| `ADMIN_PASSWORD` | `admin` | The admin's password. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | How long a login token lasts (minutes). |

## Project layout

```
app/
  main.py        starts the app, wires routers, sets up the database
  config.py      reads settings from your environment
  database.py    database connection
  security.py    passwords, login tokens, admin checks
  models/        User, Product, Review tables
  schemas/       request and response shapes
  routers/       auth, users, products, reviews
```
