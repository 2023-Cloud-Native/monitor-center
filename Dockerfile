FROM python:3.8.16-slim

LABEL MAINTAINER="Justin Ruan - justin900429@gmail.com"

WORKDIR /app

ADD . /app
RUN apt update && apt install -y curl
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:${APP_PORT}", "wsgi:app"]