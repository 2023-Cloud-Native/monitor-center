FROM python:3.8.16-slim

LABEL MAINTAINER="Justin Ruan - justin900429@gmail.com"

WORKDIR /app

ADD . /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD [ "flask", "--app", "app", "run", "host", "0.0.0.0", "--port", "5000"]