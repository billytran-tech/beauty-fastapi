from motor.motor_asyncio import AsyncIOMotorDatabase


class MongoDBHandler:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def insert_one(self, collection: str, data: dict):
        result = await self.db[collection].insert_one(data)
        return result.inserted_id

    async def insert_many(self, collection: str, data: list):
        result = await self.db[collection].insert_many(data)
        return result.inserted_ids

    async def find_one(self, collection: str, query: dict):
        document = await self.db[collection].find_one(query)
        return document

    async def find_many(self, collection: str, query: dict):
        cursor = self.db[collection].find(query)
        documents = await cursor.to_list(length=100)
        return documents

    async def update_one(self, collection: str, query: dict, update: dict):
        result = await self.db[collection].update_one(query, {'$set': update})
        return result.modified_count

    async def update_many(self, collection: str, query: dict, update: dict):
        result = await self.db[collection].update_many(query, {'$set': update})
        return result.modified_count

    async def delete_one(self, collection: str, query: dict):
        result = await self.db[collection].delete_one(query)
        return result.deleted_count

    async def delete_many(self, collection: str, query: dict):
        result = await self.db[collection].delete_many(query)
        return result.deleted_count
