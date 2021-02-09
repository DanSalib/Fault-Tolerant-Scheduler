import requests
import threading
import uuid

from models.task import HEARTBEAT_INTERVAL_SECONDS
from time import sleep
from utils.slave_logger import slave_logger
from utils.task_runner import TaskRunner

TASK_RETRY_SECONDS = 3

host = str(uuid.uuid4())

s_logger = slave_logger(__name__, host)

task_runner = TaskRunner(
    host=host
)


def run_tasks():
    while(1):
        task = task_runner.get_task()

        if task:
            task_runner.run_task(
                task=task
            )

            s_logger.info('Completed task {task}'.format(
                task=vars(task)
            ))
        else:
            s_logger.info('No tasks found. Re-checking in {sec} sec'.format(
                sec=TASK_RETRY_SECONDS
            ))

            for i in range(TASK_RETRY_SECONDS):
                sleep(1)


def send_heartbeat():
    while(1):
        for i in range(HEARTBEAT_INTERVAL_SECONDS):
            sleep(1)

        task_runner.send_heartbeat()


heartbeat_thread = threading.Thread(
    target=send_heartbeat
)

if __name__ == '__main__':
    heartbeat_thread.start()
    run_tasks()
