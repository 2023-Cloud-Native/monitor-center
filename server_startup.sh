#!/bin/bash

python data_collect.py &
gunicorn --bind 0.0.0.0:${APP_PORT} wsgi:app