#!/bin/bash

python api/data_collect.py &
sleep 5
gunicorn -c apps/gunicorn_config.py apps.wsgi:app
