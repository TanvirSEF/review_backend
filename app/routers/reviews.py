from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.post("", response_model=schemas.ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_product_review(
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    product_exists = db.execute(select(models.Product.id).where(models.Product.id == review.product_id)).scalar()
    if not product_exists:
        raise HTTPException(status_code=404, detail="Product not found")

    db_review = models.Review(
        product_id=review.product_id,
        user_id=current_user.id,
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
        "user": current_user.name,
    }


@router.put("/{id}", response_model=schemas.ReviewResponse)
def update_product_review(
    id: int,
    review_update: schemas.ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_review = db.execute(select(models.Review).where(models.Review.id == id)).scalar_one_or_none()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    if db_review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to edit this review")

    if review_update.rating is not None:
        db_review.rating = review_update.rating
    if review_update.comment is not None:
        db_review.comment = review_update.comment

    db.commit()
    db.refresh(db_review)

    return {
        "id": db_review.id,
        "product_id": db_review.product_id,
        "rating": db_review.rating,
        "comment": db_review.comment,
        "created_at": db_review.created_at,
        "user": current_user.name,
    }


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_review(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_review = db.execute(select(models.Review).where(models.Review.id == id)).scalar_one_or_none()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    if db_review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this review")

    db.delete(db_review)
    db.commit()
    return None
