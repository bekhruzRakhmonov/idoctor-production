web: gunicorn --bind :8000 --workers 3 --threads 2 config.wsgi:application && uvicorn config.asgi:application --host 0.0.0.0 --port 8000
# web: gunicorn --bind :8000 --workers 3 --threads 2 config.wsgi:application
# websocket: daphne -b 0.0.0.0 -p 5000 config.asgi:application
