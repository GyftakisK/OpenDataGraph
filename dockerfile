### 1. Get Linux
FROM fnndsc/ubuntu-python3

### 2. Get Java via the package manager
RUN apt-get update && apt-get install -y \
    openjdk-8-jdk \
    libyajl-dev \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash openDataGraph

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
