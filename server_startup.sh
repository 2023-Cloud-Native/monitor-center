#!/bin/bash

python api/data_collect.py &
sleep 5
gunicorn --bind 0.0.0.0:${APP_PORT} apps.wsgi:app
