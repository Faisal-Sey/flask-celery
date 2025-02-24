import os

from celery.exceptions import Reject

from app import celery, db
from app.models import Task

MAX_NUMBER_OF_TASKS = os.getenv('MAX_NUMBER_OF_TASKS')

@celery.task(bind=True)
def background_task(self, task_id):
    # Check if the maximum number of tasks is reached
    active_tasks = celery.control.inspect().active()
    if active_tasks and len(active_tasks) >= int(MAX_NUMBER_OF_TASKS):
        raise Reject('Maximum number of tasks reached')

    # Fetch the task from the database
    task = Task.query.get(task_id)
    if not task:
        raise ValueError(f"Task with ID {task_id} not found")

    # Update task status to 'running'
    task.status = 'running'
    db.session.commit()

    try:
        # Execute the task based on task_type
        if task.task_type == 'periodic':
            execute_periodic_task(task)
        elif task.task_type == 'daily':
            execute_daily_task(task)
        elif task.task_type == 'one-off':
            execute_one_off_task(task)
        elif task.task_type == 'delayed':
            execute_delayed_task(task)
        elif task.task_type == 'cron':
            execute_cron_task(task)
        else:
            raise ValueError(f"Unknown task type: {task.task_type}")

        task.status = 'completed'
        db.session.commit()

    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        db.session.commit()
        raise


# Task execution functions
def execute_periodic_task(task):
    # Implement periodic task logic here
    print("hy")

def execute_daily_task(task):
    # Implement daily task logic here
    pass

def execute_one_off_task(task):
    # Implement one-off task logic here
    pass

def execute_delayed_task(task):
    # Implement delayed task logic here
    pass

def execute_cron_task(task):
    # Implement cron-like task logic here
    pass
