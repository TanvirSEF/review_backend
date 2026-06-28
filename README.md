# ReviewDibo — Backend API

Backend service for **ReviewDibo**, a product-review platform. A small REST API for
browsing products, viewing average ratings, and managing user reviews. Built for the
ReviewDibo full-stack technical assessment.

## Tech Stack

FastAPI · Python 3.10+ · PostgreSQL · SQLAlchemy 2.0 · Pydantic v2

## Project Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI app, CORS, router wiring
│   ├── config.py        # settings (reads DATABASE_URL)
│   ├── database.py      # engine, Base, get_db()
│   ├── models/          # User, Product, Review
│   ├── schemas/         # Pydantic schemas
│   └── routers/         # products & reviews endpoints
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Setup & Run

All commands run from the `backend/` folder.

```bash
python -m venv venv
source venv/Scripts/activate        # Git Bash · use venv/bin/activate on Mac/Linux

pip install -r requirements.txt

cp .env.example .env                # then add your Postgres connection string

fastapi dev app/main.py
```

The API starts at `http://127.0.0.1:8000`. Tables are created automatically on startup, so
no migration commands are needed — just make sure the database named in `.env` exists.

## API Endpoints

| Method   | Endpoint             | What it does                          |
| -------- | -------------------- | ------------------------------------- |
| `GET`    | `/api/products`      | All products, each with avg rating    |
| `GET`    | `/api/products/{id}` | One product with its reviews          |
| `POST`   | `/api/reviews`       | Create a review (rating must be 1–5)  |
| `PUT`    | `/api/reviews/{id}`  | Update a review's rating / comment    |
| `DELETE` | `/api/reviews/{id}`  | Delete a review                       |

Create a review:

```bash
curl -X POST http://127.0.0.1:8000/api/reviews \
  -H "Content-Type: application/json" \
  -d '{ "product_id": 1, "user_id": 2, "rating": 5, "comment": "Great product!" }'
```

## Interactive Docs

While the server runs, open **http://127.0.0.1:8000/docs** for Swagger UI — click any
endpoint, hit **Try it out**, and run it live in the browser.
