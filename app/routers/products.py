from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from typing import List

from app import models, schemas
from app.database import get_db
from app.security import get_current_admin

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
            func.count(models.Review.id).label("review_count"),
        )
        .select_from(models.Product)
        .outerjoin(models.Review)
        .group_by(models.Product.id)
    )

    results = db.execute(query).mappings().all()
    return results


@router.post("", response_model=schemas.ProductListResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    db_product = models.Product(
        title=product.title,
        description=product.description,
        image_url=product.image_url,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


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
            "user_id": review.user_id,
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
