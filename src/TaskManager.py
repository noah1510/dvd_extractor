import threading
from enum import Enum
import os.path
import subprocess
from abc import ABC, abstractmethod
from typing import Dict, List


class TaskStatus(Enum):
    PENDING = 1
    RUNNING = 2
    COMPLETE = 3
    FAILED = 4


class Task(ABC):
    def __init__(self):
        self._process_thread: threading.Thread = None
        self._status: TaskStatus = TaskStatus.PENDING
        self._cwd = os.getcwd()
        pass

    def __del__(self):
        self.kill()

    def kill(self):
        if self._status == TaskStatus.RUNNING:
            self._process_thread.join()
            self._process_thread = None
            self._status = TaskStatus.FAILED

    def get_status(self):
        return self._status

    @abstractmethod
    def execute(self):
        pass

    def _process_thread_func(self, args: Dict):
        try:
            print(f"Running process: {args}")
            result = subprocess.run(*args['popenargs'], input=args['input'], cwd=args['cwd'], **args['kwargs'])
        except Exception as e:
            print(f"Error: {e}")
            self._status = TaskStatus.FAILED
            TaskManager.notify_status_change(self)
            return

        print(f"Process complete: {result}")
        self._status = TaskStatus.COMPLETE
        TaskManager.notify_status_change(self)

    def _internal_execute(self, *popenargs, input=None, **kwargs):
        self._status = TaskStatus.RUNNING
        TaskManager.notify_status_change(self)

        args = {
            "popenargs": popenargs,
            "input": input,
            "kwargs": kwargs,
            "cwd": self._cwd
        }
        self._process_thread = threading.Thread(
            target=self._process_thread_func,
            args=(args, ),
        )
        self._process_thread.start()


class TaskManager:
    _tasks: List[Task] = []
    _running_tasks: List[Task] = []
    _max_parallel_tasks: int = 1

    @staticmethod
    def add_task(task: Task):
        if not isinstance(task, Task):
            raise ValueError("task must be an instance of Task")

        if not task:
            raise ValueError("task must not be None")

        if task in TaskManager._tasks:
            raise ValueError("task already exists in TaskManager")

        if task.get_status() != TaskStatus.PENDING:
            raise ValueError("task must be in PENDING status to be added to TaskManager")

        TaskManager.notify_status_change(task)

    @staticmethod
    def _finish_task(task: Task):
        if task in TaskManager._running_tasks:
            TaskManager._running_tasks.remove(task)

        if len(TaskManager._running_tasks) < TaskManager._max_parallel_tasks:
            for t in TaskManager._tasks:
                if t.get_status() == TaskStatus.PENDING:
                    t.execute()

    @staticmethod
    def notify_status_change(task: Task):
        match(task.get_status()):
            case TaskStatus.COMPLETE:
                TaskManager._finish_task(task)
            case TaskStatus.FAILED:
                TaskManager._finish_task(task)
            case TaskStatus.RUNNING:
                TaskManager._running_tasks.append(task)
            case TaskStatus.PENDING:
                TaskManager._tasks.append(task)
                if len(TaskManager._running_tasks) < TaskManager._max_parallel_tasks:
                    task.execute()
            case _:
                pass

    @staticmethod
    def cleanup_tasks():
        for task in TaskManager._tasks:
            if task.get_status() == TaskStatus.COMPLETE or task.get_status() == TaskStatus.FAILED:
                TaskManager._tasks.remove(task)
