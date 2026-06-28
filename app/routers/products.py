from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from typing import List

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=List[schemas.ProductListResponse])
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


@router.get("/{id}", response_model=schemas.ProductDetailResponse)
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
