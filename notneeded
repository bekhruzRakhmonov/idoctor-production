web: gunicorn --bind :8000 --workers 3 --threads 2 config.wsgi:application
websocket: daphne -b 0.0.0.0 -p 8000 config.asgi:application

