from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewBase(BaseModel):
    product_id: int
    user_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating must be between 1 and 5")
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    product_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    user: str  # reviewer's name

    class Config:
        from_attributes = True


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
