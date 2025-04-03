web: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
worker: celery -A update_script worker --loglevel=info
