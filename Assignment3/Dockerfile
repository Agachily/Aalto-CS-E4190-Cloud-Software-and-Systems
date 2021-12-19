FROM ubuntu:latest
WORKDIR /application
ARG PYTHON_VERSION
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y python${PYTHON_VERSION} && apt-get install -y python3-pip gcc pylint && pip3 install pytest nbmake && rm -rf /var/lib/apt/lists/*
