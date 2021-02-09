import random
import uuid

HEARTBEAT_INTERVAL_SECONDS = 2
TASK_TIMEOUT = HEARTBEAT_INTERVAL_SECONDS * 2
MAX_SLEEPTIME = 5


class TaskStates(object):
    def __init__(self):
        self.CREATED = 'created'
        self.RUNNING = 'running'
        self.KILLED = 'killed'
        self.SUCCESS = 'success'


class Task(object):
    def __init__(self, taskname=str(), sleeptime=int(), state=TaskStates().CREATED, host=None):
        self.taskname = taskname
        self.sleeptime = sleeptime
        self.state = state
        self.host = host

    def generate_random_task(self):
        self.taskname = str(uuid.uuid4())
        self.sleeptime = random.randrange(
            start=1,
            stop=MAX_SLEEPTIME
        )
        self.state = TaskStates().CREATED

        return self

    def convert_json_to_task(self, task_json):
        for attr in task_json:
            if hasattr(self, attr):
                setattr(
                    self,
                    attr,
                    task_json[attr]
                )
        return self
