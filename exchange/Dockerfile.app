FROM ubuntu:20.04

RUN set -e && \
    apt-get update -q -y --no-install-recommends && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -q -y --no-install-recommends \
      ca-certificates \
      python3 \
      python3-pip \
      uwsgi \
      uwsgi-plugin-python3 \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt


RUN groupadd -r exchange -g 1000 && \
    adduser --uid 1000 --gid 1000 --system --disabled-password exchange

USER exchange
WORKDIR /home/exchange
ENV TZ="UTC"

COPY lib/requirements.txt .
RUN pip3 install -r requirements.txt
COPY app/requirements.txt .
RUN pip3 install -r requirements.txt

COPY app/ .
COPY lib lib
