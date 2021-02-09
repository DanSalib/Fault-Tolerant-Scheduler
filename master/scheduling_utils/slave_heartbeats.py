from datetime import datetime
from models.task import TASK_TIMEOUT


class SlaveHeartbeat(object):
    def __init__(self, host, taskname):
        self.host = host
        self.current_taskname = None
        self.last_heartbeat = None

        self.update_heartbeat(
            taskname=taskname
        )

    def update_heartbeat(self, taskname=None, clear_taskname=False):
        self.last_heartbeat = datetime.utcnow().timestamp()
        if taskname:
            self.current_taskname = taskname
        if clear_taskname:
            self.current_taskname = None

    def is_timed_out(self):
        return datetime.utcnow().timestamp() - self.last_heartbeat > TASK_TIMEOUT
