# Multistage docker build, requires docker 17.05

# builder stage
FROM ubuntu:20.04 as builder
ARG BITCOIN_GIT_TAG="latest"

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
        byacc \
        flex


WORKDIR /src
RUN git clone --recursive https://github.com/bitcoin/bitcoin.git && \
    cd bitcoin && \
    if [ "x$BITCOIN_GIT_TAG" = "xlatest" ]; then BITCOIN_GIT_TAG=$(git describe --tags $(git rev-list --tags --max-count=1)); fi && \
    git checkout $BITCOIN_GIT_TAG && \
    git submodule sync && git submodule update --init --force --recursive

#RUN cd bitcoin/depends && \
#    make -j$(nproc)

RUN cd bitcoin && \
    ./autogen.sh && \
    ./configure --prefix=$PWD/depends/x86_64-pc-linux-gnu && \
    make -j$(nproc)

# ---

# runtime stage
FROM ubuntu:20.04

COPY --from=0 /src/bitcoin/src/bitcoin-util \
              /src/bitcoin/src/bitcoin-cli \
              /src/bitcoin/src/bitcoin-tx \
              /src/bitcoin/src/bitcoin-wallet \
              /src/bitcoin/src/bitcoind \
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

RUN groupadd -r bitcoin -g 1000 && \
    adduser --uid 1000 --gid 1000 --system --disabled-password bitcoin && \
	mkdir -p /home/bitcoin/.bitcoin && \
	chown -R bitcoin:bitcoin /home/bitcoin/.bitcoin

USER bitcoin
WORKDIR /home/bitcoin
ENV TZ="UTC"

ENV http_proxy=socks5h://10.1.0.2:9050
ENV https_proxy=socks5h://10.1.0.2:9050

EXPOSE 8333 18333 8332
VOLUME /home/bitcoin/.bitcoin

COPY entrypoint.sh /
