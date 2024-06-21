from typing import List
from pydantic import BaseModel, Field
from .message import Message
from bson import ObjectId


class User(BaseModel):
    userId: str = Field(default_factory=lambda: str(ObjectId()), alias='_id')
    username: str
    hashed_password: str
    messages: List[Message] = []

    class Config:
        json_encoders = {
            ObjectId: str
        }
