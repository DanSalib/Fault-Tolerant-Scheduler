import os

from dotenv import load_dotenv
from models.task import Task
from pymongo import MongoClient, errors
from test_logger import test_logger

load_dotenv()
NUM_TASKS = 100

PORT = os.getenv('MONGO_PORT')
DOMAIN = os.getenv('MONGO_DOMAIN')
TASKS_DB_NAME = os.getenv('TASKS_DB_NAME')
TASKS_COLLECTION_NAME = os.getenv('TASKS_COLLECTION_NAME')
USERNAME = os.getenv('MONGO_USERNAME')
PASSWORD = os.getenv('MONGO_PASSWORD')


def get_mongo_client():
    return MongoClient(
        host=':'.join([DOMAIN, str(PORT)]),
        serverSelectionTimeoutMS=5000,
        username=USERNAME,
        password=PASSWORD,
    )


def get_tasks_db(mongo_client, override_drop=False):
    if not override_drop and TASKS_DB_NAME in mongo_client.list_database_names():
        mongo_client.drop_database(TASKS_DB_NAME)

    return mongo_client[TASKS_DB_NAME]


def get_tasks_collection(tasks_db):
    return tasks_db[TASKS_COLLECTION_NAME]


def populate_tasks():
    mongo_client = get_mongo_client()

    tasks_db = get_tasks_db(
        mongo_client=mongo_client
    )

    tasks_collection = get_tasks_collection(
        tasks_db=tasks_db
    )

    tasks = list()
    for i in range(NUM_TASKS):
        tasks.append(vars(Task().generate_random_task()))

    tasks_collection.insert_many(tasks)


if __name__ == '__main__':
    t_logger = test_logger(__name__)
    populate_tasks()

    t_logger.info('Completed populating db with tasks')
