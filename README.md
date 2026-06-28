# ReviewDibo — Backend API

The backend service for **ReviewDibo**, a simple product-review platform. It exposes a
small REST API for browsing products, viewing aggregated ratings, and managing
user-submitted reviews.

Built as part of the Full-Stack Developer technical assessment for ReviewDibo.

---

## Tech Stack

- **FastAPI** — web framework
- **Python 3.10+**
- **PostgreSQL** — database
- **SQLAlchemy 2.0** — ORM (modern `select()` query API)
- **Pydantic v2** — request/response validation

---

## Project Structure

```
backend/
├── main.py            # FastAPI app and all API routes
├── database.py        # Engine, session, Base, and get_db() dependency
├── models.py          # ORM models: User, Product, Review
├── schemas.py         # Pydantic schemas for validation
├── .env               # Local config (not committed)
├── .env.example       # Template to copy into .env
├── requirements.txt   # Python dependencies
└── README.md
```

Each file has a single job: database wiring in `database.py`, models in `models.py`,
schemas in `schemas.py`, and routes in `main.py`. No logic is crammed into one place.

---

## Prerequisites

- Python 3.10 or newer
- PostgreSQL running locally (or a reachable remote instance)
- A database you can connect to (e.g. `reviewdibo`)

---

## Setup

All commands are run from the `backend/` directory.

### 1. Create and activate a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
# macOS / Linux
source venv/bin/activate

# Windows (Git Bash)
source venv/Scripts/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### 2. Install dependencies

Create `requirements.txt` with:

```txt
fastapi[standard]>=0.110
sqlalchemy>=2.0
psycopg2-binary>=2.9
pydantic[email]>=2.5
python-dotenv>=1.0
```

Then install:

```bash
pip install -r requirements.txt
```

### 3. Configure the database

Copy the template and fill in your real PostgreSQL credentials:

```bash
cp .env.example .env
```

```dotenv
DATABASE_URL=postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/reviewdibo
```

If `DATABASE_URL` is missing, the app refuses to start with a clear error — so a bad
config never fails silently.

### 4. Create the database (once)

The tables themselves are created automatically on startup (see below), but the database
named in `DATABASE_URL` has to exist first:

```sql
CREATE DATABASE reviewdibo;
```

---

## Running the App

Start the development server with hot reload:

```bash
fastapi dev main.py
```

It runs on `http://127.0.0.1:8000`. Check that it's up:

```bash
curl http://127.0.0.1:8000/
# {"status":"ReviewDibo API is running perfectly!"}
```

> On startup, `main.py` runs `models.Base.metadata.create_all(bind=engine)`, which creates
> the `users`, `products`, and `reviews` tables automatically if they don't exist yet — no
> manual migration needed for this assessment.

---

## API Endpoints

Base URL: `http://127.0.0.1:8000`

| Method   | Endpoint             | Description                                                          | Status           |
| -------- | -------------------- | -------------------------------------------------------------------- | ---------------- |
| `GET`    | `/`                  | Health check                                                         | `200 OK`         |
| `GET`    | `/api/products`      | All products with a rounded `average_rating`                         | `200 OK`         |
| `GET`    | `/api/products/{id}` | One product with its nested reviews and reviewer names               | `200 OK`         |
| `POST`   | `/api/reviews`       | Create a review (validates product & user; rating must be 1–5)       | `201 Created`    |
| `PUT`    | `/api/reviews/{id}`  | Update a review's rating and/or comment                              | `200 OK`         |
| `DELETE` | `/api/reviews/{id}`  | Delete a review                                                      | `204 No Content` |

A few quick examples:

```bash
# Create a review
curl -X POST http://127.0.0.1:8000/api/reviews \
  -H "Content-Type: application/json" \
  -d '{ "product_id": 1, "user_id": 2, "rating": 5, "comment": "Great product." }'

# Get a product with its reviews
curl http://127.0.0.1:8000/api/products/1

# Update a review
curl -X PUT http://127.0.0.1:8000/api/reviews/1 \
  -H "Content-Type: application/json" \
  -d '{ "rating": 4 }'
```

The `rating` field is validated to be an integer from 1 to 5. Anything outside that range
is rejected with a `422` before it touches the database.

---

## Interactive Docs (Swagger / OpenAPI)

FastAPI generates the docs straight from the code. While the server is running:

- **Swagger UI** — http://127.0.0.1:8000/docs
- **ReDoc** — http://127.0.0.1:8000/redoc

Swagger UI lets you click any endpoint, hit **Try it out**, fill in the request body, and
run it live in the browser. It's the fastest way to explore the API without writing any
code.

---

## CORS

During development the API accepts requests from any origin, so a frontend on a different
port (say a Next.js app) can talk to it without issues. Before going to production, the
allowed origins should be locked down to the real frontend domain.
