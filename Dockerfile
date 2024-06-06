# Development-Only Dockerfile
#Please note that this Dockerfile is intended strictly for development purposes.
#Containerizing Ajenti is not recommended for production environments as Ajenti
#is designed to directly access and manage the Linux server resources.
#Containerization in such a context would limit Ajenti's capabilities to manage the host system effectively.
#Use this Dockerfile for development and testing scenarios only, where full access to the server's resources is not required.

FROM ubuntu:22.04

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

RUN mkdir -p /opt/ajenti/backend/ajenti-core
WORKDIR /opt/ajenti/backend

COPY ajenti-core/requirements.txt ajenti-core/requirements.txt

RUN pip3 install --upgrade pip && \
    pip3 install -r ajenti-core/requirements.txt

ENTRYPOINT ["make", "rundev"]

