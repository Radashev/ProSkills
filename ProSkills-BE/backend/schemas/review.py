from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ReviewBase(BaseModel):
    text: str


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(ReviewBase):
    pass


class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    course_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ReviewWithUserInfo(ReviewResponse):
    user_first_name: str
    user_last_name: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True) 