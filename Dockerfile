FROM node:16-buster AS node-builder
FROM ubuntu:22.04 AS ubuntu-builder
FROM python:3.10-slim-buster AS final-image



RUN apt-get update && \
    apt-get install -y \
        build-essential \
        python3-dev \
        python3-pip \
        libssl-dev \
        git \
        make \
        curl \
        sudo && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --upgrade pip setuptools

RUN mkdir -p /opt/ajenti/backend
WORKDIR /opt/ajenti/backend

COPY . .

RUN pip3 install -r ./ajenti-core/requirements.txt

ENTRYPOINT ["make", "run"]
