from datetime import timedelta

from celery.schedules import crontab
from flask import render_template, request, redirect, url_for, flash
from app import app, db, celery
from app.models import Task
from app.tasks import background_task

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/create_task', methods=['POST'])
def create_task():
    name = request.form.get('name')
    task_type = request.form.get('task_type')
    scheduled_time = request.form.get('scheduled_time')
    interval = request.form.get('interval')
    delay = request.form.get('delay')
    cron_expression = request.form.get('cron_expression')

    new_task = Task(
        name=name,
        task_type=task_type,
        scheduled_time=scheduled_time,
    )
    db.session.add(new_task)
    db.session.commit()

    if task_type == 'periodic':
        print("interval", interval)
        celery.conf.beat_schedule[f'task-{new_task.id}'] = {
            'task': 'app.tasks.background_task',
            'schedule': timedelta(seconds=int(interval)),
            'args': [new_task.id],
        }
        print(f"Updated beat schedule: {celery.conf.beat_schedule}")
    elif task_type == 'daily':
        hour, minute = map(int, scheduled_time.split(':'))
        celery.conf.beat_schedule[f'task-{new_task.id}'] = {
            'task': 'app.tasks.background_task',
            'schedule': crontab(hour=str(hour), minute=str(minute)),
            'args': [new_task.id],
        }
    elif task_type == 'one-off':
        background_task.delay(new_task.id)
    elif task_type == 'delayed':
        background_task.apply_async(args=[new_task.id], countdown=int(delay))
    elif task_type == 'cron':
        celery.conf.beat_schedule[f'task-{new_task.id}'] = {
            'task': 'app.tasks.background_task',
            'schedule': crontab(minute=cron_expression.split()[0], hour=cron_expression.split()[1]),
            'args': [new_task.id],
        }

    flash('Task created successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    return redirect(url_for('index'))