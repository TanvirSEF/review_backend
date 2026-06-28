import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Fail fast if the connection string is missing — never run with a half-configured DB.
if not DATABASE_URL:
    raise ValueError("CRITICAL ERROR: DATABASE_URL environment variable is missing!")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # drop stale connections before reusing them
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Yields a database session for each request and makes sure it gets closed.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
