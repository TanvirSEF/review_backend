# ReviewDibo API

Backend for **ReviewDibo**, a product review app. Users can browse products, see average
ratings, and write reviews. To post or edit a review you need to log in, and only admins
can add, edit, and delete products.

## Stack

FastAPI, PostgreSQL, SQLAlchemy 2.0, Pydantic v2, bcrypt (password hashing), PyJWT (login
tokens).

## How to run

There are two ways to run this. Docker is the easy one.

### With Docker (the easy way)

Make sure [Docker](https://www.docker.com/) is installed, then run these two commands:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

That's it. The database and the API start together, and the API is on http://localhost:8000.

The `POSTGRES_*` settings are already filled in for you. Change the password if you want a
stronger one. You don't need to set `DATABASE_URL`, Docker handles that.

The first run takes a little longer because Docker has to download the images.

### Without Docker (use your own Postgres)

You'll need Python 3.11+ and PostgreSQL 14+ on your machine.

1. Create the database. The app builds its tables itself, but the database has to exist
   first:

   ```powershell
   psql -U postgres -c "CREATE DATABASE reviewdibo;"
   ```

2. Make a virtual environment and install the packages:

   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. Copy the settings file:

   ```powershell
   Copy-Item .env.example .env
   ```

4. Open `.env` and fill in two things. First, `DATABASE_URL`, your database link. Replace
   the username and password with your own Postgres ones:

   ```
   postgresql://USER:PASSWORD@localhost:5432/reviewdibo
   ```

   Second, `JWT_SECRET`, a random string. Make one like this:

   ```powershell
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. Run the app:

   ```powershell
   fastapi dev app/main.py
   ```

The API is on http://127.0.0.1:8000 and the docs are at http://127.0.0.1:8000/docs.

If PowerShell blocks the activation script, run this once:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. On macOS or Linux, use
`source venv/bin/activate` instead.

## Admin account

The app needs an admin to add products. On the first start it creates one from
`ADMIN_EMAIL` and `ADMIN_PASSWORD` in your `.env`. If you leave them, it uses these:

- Email: `admin@reviewdibo.com`
- Password: `admin`

This only happens once. Later restarts won't change it. Set a strong `ADMIN_PASSWORD`
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
- `PUT /api/products/{id}` — edit a product
- `DELETE /api/products/{id}` — delete a product

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
