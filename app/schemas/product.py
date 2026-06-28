from pydantic import BaseModel
from typing import List, Optional

from app.schemas.review import ReviewResponse


class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductListResponse(ProductBase):
    id: int
    average_rating: float = 0.0

    class Config:
        from_attributes = True


class ProductDetailResponse(ProductBase):
    id: int
    reviews: List[ReviewResponse] = []

    class Config:
        from_attributes = True
