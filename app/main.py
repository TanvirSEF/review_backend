import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import products, reviews

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ready.")
    except Exception as e:
        logger.error("Could not connect to the database: %s", e)
    yield


app = FastAPI(
    title="ReviewDibo API Module",
    description="Product review API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(reviews.router)


@app.get("/")
def read_root():
    return {"status": "ReviewDibo API is running perfectly!"}
