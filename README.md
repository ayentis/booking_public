# booking

Locale

To create message files, you use the 'django-admin makemessages' tool. 

Update: python manage.py makemessages -l ua --ignore=venv 

You can also run django-admin compilemessages 

Deploy

https://developer.mozilla.org/ru/docs/Learn/Server-side/Django/Deployment

pip freeze > requirements.txt

heroku run python manage.py migrate

git add -A

git commit -m "Added files and changes required for deployment to heroku"

git push origin master

git push heroku master


celery -A site_settings.tasks worker -l info -E --concurrency 1 -P solo

worker: celery -A site_settings.tasks worker -l info

#on heroku
heroku run celery ....