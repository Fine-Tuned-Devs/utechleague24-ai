from motor.motor_asyncio import AsyncIOMotorClient
from core.config import mongodb_settings

client = AsyncIOMotorClient(mongodb_settings.MONGODB_URL)
database = client[mongodb_settings.MONGODB_DATABASE]

users_collection = database.get_collection("users")
messages_collection = database.get_collection("messages")
text_files_collection = database.get_collection("text_files")


# Startup tasks
async def initialize_database():
    await create_indexes()


async def create_indexes():
    await users_collection.create_index("username", unique=True)
    await messages_collection.create_index("sender", unique=False)
    await text_files_collection.create_index("title", unique=True)
