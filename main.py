from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from typing import List

import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ReviewDibo API Module",
    description="Full Stack Developer Technical Assessment APIs",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "ReviewDibo API is running perfectly!"}


@app.get("/api/products", response_model=List[schemas.ProductListResponse])
def get_all_products(db: Session = Depends(get_db)):
    query = (
        select(
            models.Product.id,
            models.Product.title,
            models.Product.description,
            models.Product.image_url,
            # average rating, 0.0 when there are no reviews yet
            func.coalesce(func.round(func.avg(models.Review.rating), 1), 0.0).label("average_rating"),
        )
        .select_from(models.Product)
        .outerjoin(models.Review)
        .group_by(models.Product.id)
    )

    results = db.execute(query).mappings().all()
    return results


@app.get("/api/products/{id}", response_model=schemas.ProductDetailResponse)
def get_product_details(id: int, db: Session = Depends(get_db)):
    product = db.execute(select(models.Product).where(models.Product.id == id)).scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found across database instances")

    reviews_query = select(models.Review).where(models.Review.product_id == id).order_by(models.Review.created_at.desc())
    reviews = db.execute(reviews_query).scalars().all()

    formatted_reviews = []
    for r in reviews:
        user_obj = db.execute(select(models.User).where(models.User.id == r.user_id)).scalar_one_or_none()
        username = user_obj.name if user_obj else "Anonymous User"

        formatted_reviews.append({
            "id": r.id,
            "product_id": r.product_id,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at,
            "user": username,
        })

    return {
        "id": product.id,
        "title": product.title,
        "description": product.description,
        "image_url": product.image_url,
        "reviews": formatted_reviews,
    }


@app.post("/api/reviews", response_model=schemas.ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_product_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    product_exists = db.execute(select(models.Product.id).where(models.Product.id == review.product_id)).scalar()
    if not product_exists:
        raise HTTPException(status_code=404, detail="Target product structure does not exist")

    user_obj = db.execute(select(models.User).where(models.User.id == review.user_id)).scalar_one_or_none()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Assigned user profile mapping not found")

    db_review = models.Review(
        product_id=review.product_id,
        user_id=review.user_id,
        rating=review.rating,
        comment=review.comment,
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    return {
        "id": db_review.id,
        "product_id": db_review.product_id,
        "rating": db_review.rating,
        "comment": db_review.comment,
        "created_at": db_review.created_at,
        "user": user_obj.name,
    }


@app.put("/api/reviews/{id}", response_model=schemas.ReviewResponse)
def update_product_review(id: int, review_update: schemas.ReviewUpdate, db: Session = Depends(get_db)):
    db_review = db.execute(select(models.Review).where(models.Review.id == id)).scalar_one_or_none()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review item sequence not tracked")

    if review_update.rating is not None:
        db_review.rating = review_update.rating
    if review_update.comment is not None:
        db_review.comment = review_update.comment

    db.commit()
    db.refresh(db_review)

    user_name = db.execute(select(models.User.name).where(models.User.id == db_review.user_id)).scalar() or "Anonymous"

    return {
        "id": db_review.id,
        "product_id": db_review.product_id,
        "rating": db_review.rating,
        "comment": db_review.comment,
        "created_at": db_review.created_at,
        "user": user_name,
    }


@app.delete("/api/reviews/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_review(id: int, db: Session = Depends(get_db)):
    db_review = db.execute(select(models.Review).where(models.Review.id == id)).scalar_one_or_none()
    if not db_review:
        raise HTTPException(status_code=404, detail="Requested review structure missing from nodes")

    db.delete(db_review)
    db.commit()
    return None
