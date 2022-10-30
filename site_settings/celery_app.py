from __future__ import absolute_import, unicode_literals

import logging

import os
from celery import Celery

logger = logging.getLogger('booking_console')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_settings.settings')

# BASE_REDIS_URL = os.environ.get('BROKER_URL', None)

app = Celery(__name__)

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# app.conf.broker_url = settings.BROKER_URL

# this allows you to schedule items in the Django admin.
# app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'

logger.error(f"load celery tasks")