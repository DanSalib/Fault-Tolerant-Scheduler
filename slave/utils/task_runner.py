import os
import requests

from models.task import Task, HEARTBEAT_INTERVAL_SECONDS
from time import sleep
from utils.slave_logger import slave_logger


class TaskRunner(object):
    def __init__(self, host):
        self._s_logger = slave_logger(__name__, host)

        self._MASTER_DOMAIN = os.getenv('MASTER_DOMAIN')
        self._MASTER_PORT = os.getenv('MASTER_PORT')
        self._TASK_API_ENDPOINT = 'slave/task'
        self._HEARTBEAT_API_ENDPOINT = 'slave/heartbeat'

        self._host = host

        self._DEFAULT_HEADERS = {
            'host': host
        }

    def get_task(self):
        try:
            task_response = requests.get(
                url='http://{domain}:{port}/{endpoint}'.format(
                    domain=self._MASTER_DOMAIN,
                    port=self._MASTER_PORT,
                    endpoint=self._TASK_API_ENDPOINT
                ),
                headers=self._DEFAULT_HEADERS
            )

            task_response.raise_for_status()

            if task_response.status_code == 204:
                return None

            return Task().convert_json_to_task(
                task_json=task_response.json()
            )

        except Exception as e:
            self._s_logger.exception('Encountered exception while getting task. {e}'.format(
                e=e
            ))

        return None

    def run_task(self, task):
        self._s_logger.info('Running task {task}'.format(
            task=vars(task)
        ))

        sleep(task.sleeptime)

    def send_heartbeat(self):
        try:
            heartbeat_response = requests.post(
                url='http://{domain}:{port}/{endpoint}'.format(
                    domain=self._MASTER_DOMAIN,
                    port=self._MASTER_PORT,
                    endpoint=self._HEARTBEAT_API_ENDPOINT
                ),
                headers=self._DEFAULT_HEADERS
            )

            heartbeat_response.raise_for_status()
        except Exception as e:
            self._s_logger.exception('Encountered exception while sending heartbeat. {e}'.format(
                e=e
            ))
