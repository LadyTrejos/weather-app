FROM ubuntu:bionic

ARG DEBIAN_FRONTEND=noninteractive

RUN \
 apt-get update \
 && apt-get install -y -q curl gnupg \
 && curl -sSL 'http://p80.pool.sks-keyservers.net/pks/lookup?op=get&search=0x8AA7AF1F1091A5FD' | apt-key add -  \
 && echo 'deb [arch=amd64] http://repo.sawtooth.me/ubuntu/chime/stable bionic universe' >> /etc/apt/sources.list \
 && apt-get update

RUN \
 apt-get install -y -q --no-install-recommends \
    apt-utils \
 && apt-get install -y -q \
    apt-transport-https \
    build-essential \
    ca-certificates \
    libffi-dev \
    libssl-dev \
    python3-cbor \
    python3-colorlog \
    python3-dev \
    python3-pip \
    python3-requests \
    python3-secp256k1 \
    python3-setuptools-scm \
    python3-yaml \
    python3-zmq \
    software-properties-common \
    python3-sawtooth-sdk \
    python3-sawtooth-cli \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /project/app
COPY . .
ENV PATH=$PATH:/project/app/bin
RUN ls

EXPOSE 3000
EXPOSE 4004/tcp

CMD echo "\033[0;32m--- Building weather tp ---\n\033[0m" \
   && unset PYTHONPATH \
   && python3 setup.py clean --all \
   && python3 setup.py build \
   && python3 setup.py install \
   && ['weather-tp', '-vv', '-C tcp://validator:4004']
