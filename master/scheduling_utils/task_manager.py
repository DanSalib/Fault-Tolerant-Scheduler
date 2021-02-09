import os

from models.task import Task, TaskStates
from pymongo import ReturnDocument
from utils.mongo_manager import MongoManager
from utils.master_logger import master_logger


class TaskManager(object):
    def __init__(self, heartbeat_manager):
        self._m_logger = master_logger(__name__)

        self._TASKS_DB_NAME = os.getenv('TASKS_DB_NAME')
        self._TASKS_COLLECTION_NAME = os.getenv('TASKS_COLLECTION_NAME')

        self._heartbeat_manager = heartbeat_manager
        self._mongo_manager = MongoManager()

        self._tasks_collection = None
        self.reload_collection()

    def reload_collection(self):
        self._m_logger.info('Reloading collection instance')
        self._tasks_collection = self._mongo_manager.get_collection(
            db_name=self._TASKS_DB_NAME,
            collection_name=self._TASKS_COLLECTION_NAME
        )

        self.track_running_host_heartbeats()

    def track_running_host_heartbeats(self):
        if self._tasks_collection:
            running_tasks_json = self._tasks_collection.find(
                filter={
                    'state': TaskStates().RUNNING
                }
            )

            for running_task_json in running_tasks_json:
                self._m_logger.info('Found running hosts to track')
                running_task = Task().convert_json_to_task(running_task_json)
                self._heartbeat_manager.save_new_heartbeat(
                    host=running_task.host,
                    taskname=running_task.taskname
                )

    def get_any_created_or_killed_task(self, host):
        try:
            if not self._tasks_collection:
                self.reload_collection()

            if self._tasks_collection:
                task_json = self._tasks_collection.find_one_and_update(
                    filter={
                        "$or":
                        [
                            {
                                'state': TaskStates().CREATED
                            },
                            {
                                'state': TaskStates().KILLED
                            }
                        ]
                    },
                    update={
                        '$set': {
                            'state': TaskStates().RUNNING,
                            'host': host
                        }
                    },
                    return_document=ReturnDocument.AFTER
                )

                if task_json:
                    self._m_logger.info('Running task {task}'.format(
                        task=task_json
                    ))

                    return Task().convert_json_to_task(
                        task_json=task_json
                    )

        except Exception as e:
            self._m_logger.exception('Encountered exception while getting task. {e}'.format(
                e=e
            ))

        self.get_completion_stats()

        return None

    def get_completion_stats(self):
        if self._tasks_collection:
            success_count = self._tasks_collection.count_documents(
                filter={
                    'state': TaskStates().SUCCESS
                }
            )

            not_complete_count = self._tasks_collection.count_documents(
                filter={
                    'state': {
                        '$ne': TaskStates().SUCCESS
                    }
                }
            )

            total_count = self._tasks_collection.count()

            self._m_logger.info('No more tasks found. Success count={success}, Not complete count={not_complete}, Total count={total}'.format(
                success=success_count,
                not_complete=not_complete_count,
                total=total_count
            ))

    def end_task(self, taskname, is_success):
        try:
            if self._tasks_collection and taskname:
                status = TaskStates().SUCCESS if is_success else TaskStates().KILLED

                self._tasks_collection.find_one_and_update(
                    filter={
                        'taskname': taskname
                    },
                    update={
                        '$set': {
                            'state': status,
                        }
                    },
                    return_document=ReturnDocument.AFTER
                )

                self._m_logger.info('Ended task {taskname} with status {status}'.format(
                    taskname=taskname,
                    status=status
                ))
        except Exception as e:
            self._m_logger.exception('Encountered exception while getting task. {e}'.format(
                e=e
            ))
