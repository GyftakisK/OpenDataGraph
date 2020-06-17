### 1. Get Linux
FROM alpine:3.7

### 2. Get Java via the package manager
RUN apk add --update \
    bash \
    python3 \
    python3-dev \
    py-pip \
    build-base \
    openjdk8-jre \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    yajl-dev \
    openssl-dev \
  && rm -rf /var/cache/apk/*

RUN adduser -D openDataGraph

WORKDIR /home/openDataGraph
RUN mkdir db

COPY requirements.txt requirements.txt
RUN python3 -m venv venv
RUN venv/bin/pip install --upgrade pip setuptools
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY db_manager db_manager
COPY harvesters harvesters
COPY knowledge_extractor knowledge_extractor
COPY medknow medknow
COPY boot.sh celery_worker.py config.py disease_graph_run_app.py utilities.py ./

RUN chown -R openDataGraph:openDataGraph ./
RUN chmod +x boot.sh
USER openDataGraph

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
