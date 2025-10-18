import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "audio_analysis")
COLL = "analyses"

client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorClient] = None
collection: Optional[AsyncIOMotorClient] = None

async def init_db():
    """Initialize MongoDB client and collection."""
    global client, db, collection
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[COLL]
    return DBWrapper(collection)

def get_db():
    """Return a wrapper around the MongoDB collection."""
    if collection is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return DBWrapper(collection)

class DBWrapper:
    def __init__(self, col):
        self.col = col

    async def insert_one(self, doc: dict):
        await self.col.insert_one(doc)

    async def update_one(self, query: dict, update: dict):
        await self.col.update_one(query, update)

    async def find_one(self, query: dict):
        return await self.col.find_one(query)

    async def find(self, query: dict = {}, limit: int = 50, sort: Optional[list] = None):
        cursor = self.col.find(query)
        if sort:
            cursor = cursor.sort(sort)
        items = []
        async for d in cursor:
            items.append(d)
            if len(items) >= limit:
                break
        return items
