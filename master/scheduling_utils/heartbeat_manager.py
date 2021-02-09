from datetime import datetime
from models.task import TASK_TIMEOUT, TaskStates
from scheduling_utils.slave_heartbeats import SlaveHeartbeat
from utils.master_logger import master_logger


class HeartbeatManager(object):
    def __init__(self):
        self._m_logger = master_logger(__name__)
        self.heartbeats = dict()

    def get_host_existing_taskname(self, host):
        if host in self.heartbeats:
            return self.heartbeats[host].current_taskname

        return None

    def save_new_heartbeat(self, host, taskname=None, clear_taskname=False):
        if host in self.heartbeats:
            self.heartbeats[host].update_heartbeat(
                taskname=taskname,
                clear_taskname=clear_taskname
            )
        else:
            self.heartbeats[host] = SlaveHeartbeat(
                host=host,
                taskname=taskname
            )

    def get_timed_out_slave_tasks(self):
        timed_out_slave_tasks = list()

        for host in list(self.heartbeats):
            if self.heartbeats[host].is_timed_out():
                timed_out_slave_tasks.append(
                    self.heartbeats[host].current_taskname
                )
                del self.heartbeats[host]

        return timed_out_slave_tasks
