import os

from celery.exceptions import Reject

from app import celery, db
from app.models import Task
import time

MAX_NUMBER_OF_TASKS = os.getenv('MAX_NUMBER_OF_TASKS')

@celery.task
def background_task(task_id):
    active_tasks = celery.control.inspect().active()
    if active_tasks and len(active_tasks) >= int(MAX_NUMBER_OF_TASKS):
        raise Reject('Maximum number of tasks reached')

    task = Task.query.get(task_id)
    if task:
        task.status = 'running'
        db.session.commit()

        # Simulate a long-running task
        time.sleep(10)

        task.status = 'completed'
        db.session.commit()