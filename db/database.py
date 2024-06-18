from motor.motor_asyncio import AsyncIOMotorClient
from core.config import mongodb_settings

client = AsyncIOMotorClient(mongodb_settings.MONGODB_URL)
database = client[mongodb_settings.MONGODB_DATABASE]

users_collection = database.get_collection("users")


# Startup tasks
async def initialize_database():
    await create_indexes()


async def create_indexes():
    await users_collection.create_index("username", unique=True)
