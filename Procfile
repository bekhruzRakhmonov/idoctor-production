web: gunicorn --bind :8000 --workers 3 --threads 2 config.wsgi:application
websocket: gunicorn myproject.asgi:application -k uvicorn.workers.UvicornWorker
