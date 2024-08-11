import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection


class MongoDBManager:
    _instance = None

    def __new__(cls, uri: str = 'mongodb://localhost:27017/', database_name: str = 'test'):
        if cls._instance is None:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
            cls._instance._client = MongoClient(uri)
            cls._instance._database = cls._instance._client[database_name]
        return cls._instance

    def get_collection(self, collection_name: str) -> Collection:
        return self._database[collection_name]

    def insert_one(self, collection_name: str, document: dict) -> None:
        collection = self.get_collection(collection_name)
        collection.insert_one(document)

    def find_one(self, collection_name: str, query: dict) -> dict:
        collection = self.get_collection(collection_name)
        return collection.find_one(query)

    def find_all(self, collection_name: str, query: dict) -> dict:
        collection = self.get_collection(collection_name)
        return collection.find(query)

    def update_one(self, collection_name: str, query: dict, operation: str, update: dict) -> None:
        collection = self.get_collection(collection_name)
        collection.update_one(query, {f'${operation}': update})

    def delete_one(self, collection_name: str, query: dict) -> None:
        collection = self.get_collection(collection_name)
        collection.delete_one(query)

    def close(self):
        self._client.close()


def get_db():
    load_dotenv()
    return MongoDBManager(os.getenv("DATABASE_URI"), os.getenv("DATABASE_NAME"))
