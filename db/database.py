from motor.motor_asyncio import AsyncIOMotorClient
from core.config import mongodb_settings
import asyncio

client = AsyncIOMotorClient(mongodb_settings.MONGODB_URL)
database = client[mongodb_settings.MONGODB_DATABASE]

users_collection = database.get_collection("users")


# Ensure a unique index on the username field
async def create_indexes():
    await users_collection.create_index("username", unique=True)


asyncio.run(create_indexes())
