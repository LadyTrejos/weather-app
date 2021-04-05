FROM ubuntu:bionic

RUN \
 apt-get update; \
 apt-get install -y -q curl gnupg \
 && apt-get update \
 && apt-get install -y -q \
    apt-transport-https \
    build-essential \
    ca-certificates \
    python3-pip \
    libssl-dev \
    build-essential \
    automake \
    pkg-config \
    libtool \
    libffi-dev \
    libgmp-dev \
    libyaml-cpp-dev \
    libsecp256k1-0 \
    libsecp256k1-dev \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install \
    cbor pyyaml sawtooth-sdk requests

EXPOSE 4004/tcp

WORKDIR /project/app
COPY . .
RUN ls
ENV PATH "$PATH:/project/app"

CMD \
bash -c './weather-processor'