import os
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS') == 'True'  # Fix boolean parsing
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND')
app.config['CELERY_BEAT_SCHEDULE'] = {}
app.config['CELERY_INCLUDE'] = ['app.tasks']
app.config['CELERY_TIMEZONE'] = 'UTC'
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Import routes and models
from app import routes, models