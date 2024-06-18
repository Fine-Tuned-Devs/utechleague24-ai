from db.models.user import UserInDB
from db.database import users_collection
from core.security import get_password_hash


async def get_user_by_username(username: str):
    user = await users_collection.find_one({"username": username})
    if user:
        return UserInDB(**user)


async def create_user(username: str, password: str):
    hashed_password = get_password_hash(password)
    user = UserInDB(username=username, hashed_password=hashed_password)
    await users_collection.insert_one(user.dict())
    return user
