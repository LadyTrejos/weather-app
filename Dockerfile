FROM ubuntu:bionic

# ARG DEBIAN_FRONTEND=noninteractive

# RUN \
# #  apt-get update \
# #  && apt-get install -y -q curl gnupg \
# #  && curl -sSL 'http://p80.pool.sks-keyservers.net/pks/lookup?op=get&search=0x8AA7AF1F1091A5FD' | apt-key add -  \
# #  && echo 'deb [arch=amd64] http://repo.sawtooth.me/ubuntu/chime/stable bionic universe' >> /etc/apt/sources.list \
#  apt-get update \
#  && apt-get install -y -q \
#     apt-transport-https \
#     build-essential \
#     ca-certificates \
#     python3-sawtooth-sdk \
#     python3-protobuf \
#     python3-pandas \
#  && apt-get clean \
#  && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y -q \
    python3.6 \ 
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
    libsecp256k1-dev

RUN pip3 install \
    cbor pyyaml sawtooth-sdk

EXPOSE 4004/tcp

RUN ls
WORKDIR /project/app
ENV PATH "$PATH:/project/app"
RUN ls 

CMD \
echo "\033[0;32m--- Building weather-tp ---\n\033[0m" \
&& python3 main.py