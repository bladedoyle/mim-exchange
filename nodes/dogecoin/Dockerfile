# Multistage docker build, requires docker 17.05

# builder stage
FROM ubuntu:20.04 as builder
ARG DOGECOIN_GIT_TAG="latest"

RUN set -e && \
    apt-get update -q -y --no-install-recommends && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -q -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        build-essential libtool autotools-dev automake pkg-config bsdmainutils python3 \
        libevent-dev libboost-dev \
        libsqlite3-dev \
        libzmq3-dev \
        systemtap-sdt-dev \
        libqrencode-dev \
        bison \
        flex


WORKDIR /src
RUN git clone --recursive https://github.com/dogecoin/dogecoin.git && \
    cd dogecoin && \
    if [ "x$DOGECOIN_GIT_TAG" = "xlatest" ]; then DOGECOIN_GIT_TAG=$(git describe --tags $(git rev-list --tags --max-count=1)); fi && \
    git checkout $DOGECOIN_GIT_TAG && \
    git submodule sync && git submodule update --init --force --recursive

RUN cd dogecoin/depends && \
    make -j$(nproc)

RUN cd dogecoin && \
    ./autogen.sh && \
    ./configure --prefix=$PWD/depends/x86_64-pc-linux-gnu && \
    make -j$(nproc)

# ---

# runtime stage
FROM ubuntu:20.04

COPY --from=0 /src/dogecoin/src/dogecoin-cli \
              /src/dogecoin/src/dogecoin-tx \
              /src/dogecoin/src/dogecoind \
                  /usr/local/bin/

RUN set -e && \
    apt-get update -q -y --no-install-recommends && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -q -y --no-install-recommends \
      ca-certificates \
      netcat \
      libevent-pthreads-2.1-7 \
      libevent-2.1-7 \
      libsqlite3-0 \
      libzmq5 \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt

RUN groupadd -r dogecoin -g 1000 && \
    adduser --uid 1000 --gid 1000 --system --disabled-password dogecoin && \
	mkdir -p /home/dogecoin/.dogecoin && \
	chown -R dogecoin:dogecoin /home/dogecoin/.dogecoin

USER dogecoin
WORKDIR /home/dogecoin
ENV TZ="UTC"

ENV http_proxy=socks5h://10.1.0.2:9050
ENV https_proxy=socks5h://10.1.0.2:9050

EXPOSE 8333 18333 8332
VOLUME /home/dogecoin/.dogecoin

ADD entrypoint.sh /
