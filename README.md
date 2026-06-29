# ReviewDibo API

Backend for **ReviewDibo**, a product-review app. Users can browse products, see average
ratings, and write reviews — with JWT auth so only logged-in users can post or edit.
Products are managed by **admins**.

## Stack

FastAPI · PostgreSQL · SQLAlchemy 2.0 · Pydantic v2. Passwords are hashed with bcrypt and
auth tokens are JWT (PyJWT).

## Run locally

```bash
python -m venv venv
source venv/bin/activate        # Git Bash on Windows: source venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env            # fill in DATABASE_URL and JWT_SECRET
fastapi dev app/main.py
```

You need a Postgres database already created (any name). The app creates the tables itself
on startup, so there's nothing to migrate. It also makes sure a default admin account
exists (see [Admin account](#admin-account)). API runs on http://127.0.0.1:8000, docs on
http://127.0.0.1:8000/docs.

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

Product management is admin-only. On startup the app creates a default admin if one
doesn't already exist, using the `ADMIN_EMAIL` / `ADMIN_PASSWORD` settings — defaults
`admin@reviewdibo.com` / `admin`.

The admin logs in through the normal login endpoint to get a JWT, then sends it as a
`Bearer` token when creating products:

```bash
# log in as admin (copy access_token out of the response)
curl -X POST localhost:8000/api/auth/login -d "username=admin@reviewdibo.com&password=admin"

# create a product with the admin token
curl -X POST localhost:8000/api/products \
  -H "Authorization: Bearer <paste-admin-token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Wireless Mouse","description":"Quiet clicks, USB-C.","image_url":"https://.../mouse.jpg"}'
```

> **Change the defaults in production.** `admin` / `admin` is a convenience for local/dev.
> In real deployments set a strong `ADMIN_PASSWORD` (and `ADMIN_EMAIL`) through environment
> variables. The seeder only creates the account on first run — rotating the password later
> means updating it in the database directly.

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

## Environment variables

| Variable | Default | Notes |
| --- | --- | --- |
| `DATABASE_URL` | — *(required)* | Postgres connection string. |
| `JWT_SECRET` | `change-me-in-production` | Set a long random string. |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins. Lock this down in prod. |
| `ADMIN_EMAIL` | `admin@reviewdibo.com` | Default admin email, seeded on startup. |
| `ADMIN_PASSWORD` | `admin` | Default admin password. Change in prod. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | JWT lifetime in minutes. |

## Try it

```bash
# register a normal user
curl -X POST localhost:8000/api/users -H "Content-Type: application/json" \
  -d '{"name":"Hasan","email":"h@e.com","password":"pass1234"}'

# log in (copy access_token out of the response)
curl -X POST localhost:8000/api/auth/login -d "username=h@e.com&password=pass1234"

# post a review with the token
curl -X POST localhost:8000/api/reviews \
  -H "Authorization: Bearer <paste-token-here>" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"rating":5,"comment":"solid"}'
```

Or just open http://127.0.0.1:8000/docs and use the **Authorize** button (works for both
regular users and the admin).
