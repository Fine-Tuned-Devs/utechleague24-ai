from typing import Optional
from bson import ObjectId

from core.security import get_password_hash
from db.database import users_collection
from db.models.message import Message
from db.models.user import User


async def get_user_by_username(username: str) -> Optional[User]:
    user = await users_collection.find_one({"username": username})
    if user:
        user['userId'] = str(user.pop('_id'))
        return User(**user)
    return None


async def get_user_by_id(user_id: str) -> Optional[User]:
    user_data = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user_data:
        user_data['userId'] = str(user_data.pop('_id'))
        return User(**user_data)
    return None


async def create_user(username: str, password: str) -> str:
    user_dict = {
        "username": username,
        "hashed_password": get_password_hash(password),
        "messages": [],
        "_id": ObjectId()  # Assign an ObjectId
    }
    result = await users_collection.insert_one(user_dict)
    return str(result.inserted_id)


async def find_message(user_id: str, message_id: str) -> Optional[Message]:
    user_data = await users_collection.find_one(
        {"_id": ObjectId(user_id), "messages._id": ObjectId(message_id)},
        {"messages.$": 1}
    )
    if user_data and "messages" in user_data:
        return Message(**user_data["messages"][0])
    return None
