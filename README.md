# ReviewDibo API

Backend for **ReviewDibo**, a product-review app. Users can browse products, see average
ratings, and write reviews — with JWT auth so only logged-in users can post or edit.

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
on startup, so there's nothing to migrate. API runs on http://127.0.0.1:8000, docs on
http://127.0.0.1:8000/docs.

## Layout

```
app/
  main.py        app + router wiring
  config.py      settings from env
  database.py    engine + session
  security.py    hashing, JWT, current user
  models/        User, Product, Review
  schemas/       Pydantic schemas
  routers/       auth, users, products, reviews
```

## Endpoints

No login needed:

- `POST /api/users` — register
- `POST /api/auth/login` — log in, get a JWT
- `POST /api/products` — add a product
- `GET /api/products` — list, each with its average rating
- `GET /api/products/{id}` — one product and its reviews

Login required (send `Authorization: Bearer <token>`):

- `POST /api/reviews` — write a review
- `PUT /api/reviews/{id}` — edit your own review
- `DELETE /api/reviews/{id}` — delete your own review

The author of a review is whoever is logged in, and you can only change your own reviews.

## Try it

```bash
# register
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

Or just open http://127.0.0.1:8000/docs and use the **Authorize** button.
