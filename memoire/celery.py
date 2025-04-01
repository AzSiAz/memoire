import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memoire.settings')

app = Celery('memoire')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure Celery to use Redis as broker and backend
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/0'

# Configure periodic tasks
app.conf.beat_schedule = {
    'summarize-memories': {
        'task': 'memory.tasks.summarize_memories',
        'schedule': 60.0,  # Run daily (24 hours in seconds)
    },
} 
