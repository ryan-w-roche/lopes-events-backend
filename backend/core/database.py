from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
import os

MONGODB_CONNECTION_URI = os.getenv("MONGODB_CONNECTION_URI")
DATABASE = os.getenv("DATABASE")

class Database:
    _client: AsyncIOMotorClient = None

    @staticmethod
    async def connect():
        Database._client = AsyncIOMotorClient(MONGODB_CONNECTION_URI)
        print("Connected to MongoDB.")

    @staticmethod
    async def close():
        if Database._client:
            Database._client.close()
            print("MongoDB connection closed.")

    @staticmethod
    @asynccontextmanager
    async def get_db():
        try:
            await Database.connect()
            yield Database._client[DATABASE]
        finally:
            await Database.close()