import os
import requests
import threading

from flask import Flask, Blueprint, request
from models.task import TASK_TIMEOUT
from time import sleep
from scheduling_utils.heartbeat_manager import HeartbeatManager
from scheduling_utils.task_manager import TaskManager
from utils.load_response import load_response
from utils.master_logger import master_logger

app = Flask(__name__)

slave_routes = Blueprint('slave_routes', __name__, url_prefix='/slave')

m_logger = master_logger(__name__)


heartbeat_manager = HeartbeatManager()

task_manager = TaskManager(
    heartbeat_manager=heartbeat_manager
)

HEARTBEAT_CHECK_INTERVAL_SECONDS = TASK_TIMEOUT + 1


def check_heartbeats(shared_heartbeat_manager):
    while(1):
        for i in range(HEARTBEAT_CHECK_INTERVAL_SECONDS):
            sleep(1)

        tasknames_to_kill = shared_heartbeat_manager.get_timed_out_slave_tasks()
        for taskname in tasknames_to_kill:
            if taskname:
                task_manager.end_task(
                    taskname=taskname,
                    is_success=False
                )


heartbeat_check_thread = threading.Thread(
    target=check_heartbeats,
    args=(heartbeat_manager, )
)

heartbeat_check_thread.start()

m_logger.info('Initialized heartbeat check thread')


def is_host_completed_existing_task(new_task, existing_taskname):
    return (
        (existing_taskname and not new_task) or
        (new_task and new_task.taskname != existing_taskname)
    )


@slave_routes.route('/task', methods=['GET'])
def send_task():
    try:
        host = request.headers.get('host')

        new_task = task_manager.get_any_created_or_killed_task(
            host=host
        )

        existing_taskname = heartbeat_manager.get_host_existing_taskname(
            host=host
        )

        if is_host_completed_existing_task(
            new_task=new_task,
            existing_taskname=existing_taskname
        ):
            task_manager.end_task(
                existing_taskname,
                is_success=True
            )

        heartbeat_manager.save_new_heartbeat(
            host=host,
            taskname=new_task.taskname if new_task else None,
            clear_taskname=new_task is None
        )

        if new_task:
            return load_response(
                data=vars(new_task),
                status_code=200
            )
        else:
            return load_response(
                data={},
                status_code=204
            )

    except Exception as e:
        m_logger.exception('Encountered exception when sending task. {e}'.format(
            e=e
        ))

    return load_response(
        data={
            'message': 'Failed to send task'
        },
        status_code=404
    )


@ slave_routes.route('/heartbeat', methods=['POST'])
def log_heartbeat():
    try:
        host = request.headers.get('host')

        heartbeat_manager.save_new_heartbeat(
            host=host,
        )

        return load_response(
            data={},
            status_code=200
        )
    except Exception as e:
        m_logger.exception('Encountered exception when logging heartbeat. {e}'.format(
            e=e
        ))

    return load_response(
        data={
            'message': 'Failed to log heartbeat'
        },
        status_code=404
    )
