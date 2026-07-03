from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    fullname: str
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    fullname: str
    username: str
    email: str

    class Config:
        from_attributes = True

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: int
    price: float

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    
class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    quantity: int
    price: float
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True