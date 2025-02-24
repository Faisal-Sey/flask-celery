from flask import render_template, request, redirect, url_for, flash
from app import app, db
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

    new_task = Task(name=name, task_type=task_type, scheduled_time=scheduled_time)
    db.session.add(new_task)
    db.session.commit()

    # Start the Celery task
    background_task.delay(new_task.id)

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