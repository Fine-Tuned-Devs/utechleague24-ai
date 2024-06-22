from datetime import datetime
from typing import Optional, List
from bson import ObjectId

from core.security import get_password_hash
from db.database import users_collection, messages_collection
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


async def create_message(username: str, content: str) -> str:
    message_dict = {
        "messageId": str(ObjectId()),
        "sender": username,
        "text": content,
        "createdAt": datetime.utcnow(),
        "likes": 0,
        "dislikes": 0,
        "rating": None,
        "alert": False
    }
    await messages_collection.insert_one(message_dict)
    return message_dict['messageId']


async def get_all_messages_by_username(username: str) -> List[Message]:
    messages = await messages_collection.find({"sender": username}).sort("createdAt", -1).to_list(length=None)
    return [Message(**{**message, 'messageId': str(message['_id']), '_id': str(message['_id'])}) for message in
            messages]


async def get_last_n_messages(username: str, n: int) -> List[Message]:
    all_messages = await get_all_messages_by_username(username)
    return all_messages[:n]  # Get the last n messages


async def get_first_n_messages(username: str, n: int) -> List[Message]:
    all_messages = await get_all_messages_by_username(username)
    return all_messages[-n:]  # Get the first n messages


async def join_messages(messages: List[Message]) -> str:
    return "\n".join(message.text for message in messages)
