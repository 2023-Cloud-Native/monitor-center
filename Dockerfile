FROM python:3.8.16-slim

LABEL MAINTAINER="Justin Ruan - justin900429@gmail.com"
LABEL name="Monitor API"
LABEL BUILD_DATE="2023/05/01"
LABEL DESCRIPTION="API for monitor reservoir, electricity, and earthquake data"

RUN apt update && apt install -y curl && \
    apt clean && rm -rf /var/lib/apt/lists/*

WORKDIR /home/nonroot
ADD . /home/nonroot
RUN pip install --no-cache-dir -r requirements.txt && \
    pip cache purge && rm requirements.txt

RUN groupadd --gid 1000 python && \
    useradd --uid 1000 --gid python -ms /bin/bash nonroot && \
    chown -R nonroot:python /home/nonroot/ 

USER nonroot
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:${APP_PORT}", "wsgi:app"]