web: gunicorn site_settings.wsgi --log-file -
worker: celery -A site_settings.tasks worker -l info