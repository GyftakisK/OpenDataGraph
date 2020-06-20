FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y \
  libyajl-dev \
  openjdk-8-jdk \
  python3-pip \
  python3-dev \
  python3-venv \
  && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash openDataGraph

WORKDIR /home/openDataGraph
RUN mkdir db

COPY requirements.txt requirements.txt
RUN python3 -m venv venv \
    && venv/bin/pip install --upgrade pip setuptools \
    && venv/bin/pip install -r requirements.txt \
    && venv/bin/pip install gunicorn

COPY . ./

RUN chown -R openDataGraph:openDataGraph ./ \
    && chmod +x boot.sh

USER openDataGraph

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
