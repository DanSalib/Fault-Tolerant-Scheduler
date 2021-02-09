import os

from models.task import Task
from pymongo import MongoClient, errors
from utils.master_logger import master_logger


class MongoManager(object):
    def __init__(self):
        self._m_logger = master_logger(__name__)

        self._PORT = os.getenv('MONGO_PORT')
        self._DOMAIN = os.getenv('MONGO_DOMAIN')
        self._USERNAME = os.getenv('MONGO_USERNAME')
        self._PASSWORD = os.getenv('MONGO_PASSWORD')

        self._client = None
        self._set_mongo_client()

        self._db = None
        self._collection_name = None
        self._collection = None

    def _set_mongo_client(self):
        self._client = MongoClient(
            host=':'.join([self._DOMAIN, str(self._PORT)]),
            serverSelectionTimeoutMS=5000,
            username=self._USERNAME,
            password=self._PASSWORD,
        )

    def _set_database(self, db_name):
        self._db = self._client[db_name] if self._client else None

    def _set_collection(self, collection_name):
        self._collection = self._db[collection_name] if self._db else None

    def get_collection(self, db_name=None, collection_name=None):
        if collection_name and self._collection_name != collection_name:
            self._set_database(db_name)
            self._set_collection(collection_name)

        return self._collection
