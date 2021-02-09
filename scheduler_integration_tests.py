import os
import pymongo
import unittest

from datetime import datetime
from models.task import TASK_TIMEOUT, TaskStates
from populate_db import get_mongo_client, get_tasks_db, get_tasks_collection, populate_tasks, NUM_TASKS
from time import sleep
from test_logger import test_logger

RUNTIME_TOLERANCE = TASK_TIMEOUT * 10
NUM_SLAVES = 3


class SchedulerIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.t_logger = test_logger(__name__)

        os.system('sh start.sh')

        self.t_logger.info('Scheduler Running')
        self.start_timestamp_seconds = datetime.utcnow().timestamp()

        mongo_client = get_mongo_client()

        tasks_db = get_tasks_db(
            mongo_client=mongo_client,
            override_drop=True
        )

        self.tasks_collection = get_tasks_collection(
            tasks_db=tasks_db
        )

        all_tasks = self.tasks_collection.find()

        self.min_runtime = int(sum(int(task['sleeptime'])
                                   for task in all_tasks)/NUM_SLAVES)

        self.t_logger.info('Min runtime: {runtime} sec'.format(
            runtime=self.min_runtime
        ))

        self.max_runtime = self.min_runtime + RUNTIME_TOLERANCE
        self.t_logger.info('Max runtime: {runtime} sec'.format(
            runtime=self.max_runtime
        ))

    def test_restart_master_and_slaves(self):
        self.t_logger.info('Restarting slave_1')

        os.system('sudo docker restart Fault-Tolerant-Scheduler_slave_1')

        sleep(self.min_runtime/10)

        self.t_logger.info('Restarting slave_3')
        os.system('sudo docker restart Fault-Tolerant-Scheduler_slave_3')

        sleep(self.min_runtime/10)

        self.t_logger.info('Restarting master')

        os.system('sudo docker restart Fault-Tolerant-Scheduler_master_1')

        sleep(self.min_runtime/10)

        self.t_logger.info('Restarting slave_2')

        os.system('sudo docker restart Fault-Tolerant-Scheduler_slave_2')

        success_count = 0
        while(success_count < NUM_TASKS and datetime.utcnow().timestamp() - self.start_timestamp_seconds < self.max_runtime):
            success_count = self.tasks_collection.count_documents(
                filter={
                    'state': TaskStates().SUCCESS
                }
            )
            sleep(1)

            self.t_logger.info('{success} tasks complete'.format(
                success=success_count
            ))

        success_count = self.tasks_collection.count_documents(
            filter={
                'state': TaskStates().SUCCESS
            }
        )

        self.t_logger.info('Total runtime: {runtime} sec'.format(
            runtime=datetime.utcnow().timestamp() - self.start_timestamp_seconds
        ))

        with open('logs/mongo_entries.txt', 'w') as f:
            for task in self.tasks_collection.find():
                f.write('{task}\n'.format(
                    task=task
                ))

        self.assertEqual(success_count, NUM_TASKS)


if __name__ == '__main__':
    unittest.main()
