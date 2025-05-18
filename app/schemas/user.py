from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
import uuid


class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str]= None
    password: Optional[str]= None
    travel_style: Optional[str]= None
    budget_range: Optional[str]= None

class UserPreferences(BaseModel):
    travel_style: Optional[str]
    budget_range: Optional[str]
    destination: List[str]=[]

class UserResponse(BaseModel):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]=None
    # preferences: UserPreferences
