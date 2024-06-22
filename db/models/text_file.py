from pydantic import BaseModel, Field
from bson import ObjectId


class TextFile(BaseModel):
    fileId: str = Field(default_factory=lambda: str(ObjectId()), alias='_id')
    title: str
    content: str

    class Config:
        json_encoders = {
            ObjectId: str
        }
