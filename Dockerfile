FROM ubuntu:bionic

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install gnupg -y

RUN echo "deb http://repo.sawtooth.me/ubuntu/nightly bionic universe" >> /etc/apt/sources.list \
 && (apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 44FC67F19B2466EA \
 || apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 44FC67F19B2466EA) \
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
ENV PYTHONPATH "${PYTHONPATH}:/project/app/weather"
RUN echo $PYTHONPATH
RUN ls

EXPOSE 3000
EXPOSE 4004/tcp

CMD echo "\033[0;32m--- Building weather tp ---\n\033[0m" \
   && python3 setup.py clean --all \
   && python3 setup.py build \
   && python3 setup.py install

# RUN ["/bin/bash", "-c", "weather-tp -vv -C tcp://validator:4004"]
