# backend/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# .env file theke environment variables load korbe
load_dotenv()

# Strict runtime validation: URL na paile system error throw korbe production security-r jonne
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("CRITICAL ERROR: DATABASE_URL environment variable is missing!")

# SQLAlchemy DB Engine configuration
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True  # Connection pooling security configuration
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI router connection session context manager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()