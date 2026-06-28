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
        raise HTTPException(status_code=404, detail="Product not found")

    rows = db.execute(
        select(models.Review, models.User.name)
        .join(models.Review.user)
        .where(models.Review.product_id == id)
        .order_by(models.Review.created_at.desc())
    ).all()

    reviews = [
        {
            "id": review.id,
            "product_id": review.product_id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at,
            "user": name,
        }
        for review, name in rows
    ]

    return {
        "id": product.id,
        "title": product.title,
        "description": product.description,
        "image_url": product.image_url,
        "reviews": reviews,
    }
