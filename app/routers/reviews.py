from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.post("", response_model=schemas.ReviewResponse, status_code=status.HTTP_201_CREATED)
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


@router.put("/{id}", response_model=schemas.ReviewResponse)
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


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_review(id: int, db: Session = Depends(get_db)):
    db_review = db.execute(select(models.Review).where(models.Review.id == id)).scalar_one_or_none()
    if not db_review:
        raise HTTPException(status_code=404, detail="Requested review structure missing from nodes")

    db.delete(db_review)
    db.commit()
    return None
