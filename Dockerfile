FROM ubuntu:latest
LABEL authors="martinhummel"

ENTRYPOINT ["top", "-b"]


# Using a multi-stage build to keep the final image as small as possible
FROM node:16-buster AS node-builder
FROM ubuntu:22.04 AS ubuntu-builder
FROM python:3.10-slim-buster AS final-image

# Set a working directory
WORKDIR /git
# Install required packages
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

# Install python packages
RUN pip3 install \
        pyyaml \
        wheel \
        jadi \
        distro \
        gevent \
        daemon \
        termcolor \
        psutil \
        arrow \
        gevent-websocket \
        pyOpenSSL \
        bs4 \
        simplejson \
        pexpect \
        gipc \
        jinja2 \
        qrcode \
        reconfigure \
        itsdangerous \
        pyotp \
        setproctitle


RUN git clone https://github.com/ajenti/ajenti.git /git/ajenti && \
    cd /git/ajenti && \
    git checkout fstab


RUN mkdir -p /etc/ajenti/ && \
    touch /etc/ajenti/users.yml


WORKDIR /git/ajenti

# Set the default command to run when the container starts
CMD ["make", "rundev"]
