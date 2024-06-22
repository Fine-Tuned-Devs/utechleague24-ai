from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class Message(BaseModel):
    messageId: str = Field(default_factory=lambda: str(ObjectId()), alias='_id')
    sender: str
    text: str
    is_user: bool = True
    createdAt: datetime
    likes: int = 0
    dislikes: int = 0
    rating: Optional[int] = None
    alert: bool = False

    class Config:
        json_encoders = {
            ObjectId: str
        }
