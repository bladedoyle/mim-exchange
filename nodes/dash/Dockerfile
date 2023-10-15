# Multistage docker build, requires docker 17.05

# builder stage
FROM ubuntu:20.04 as builder
ARG DASH_GIT_TAG="latest"

RUN set -e && \
    apt-get update -q -y --no-install-recommends && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -q -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        build-essential libtool autotools-dev automake pkg-config bsdmainutils python3 \
        bison \
        flex


WORKDIR /src
RUN git clone --recursive https://github.com/dashpay/dash.git && \
    cd dash && \
    if [ "x$DASH_GIT_TAG" = "xlatest" ]; then DASH_GIT_TAG=$(git describe --tags $(git rev-list --tags --max-count=1)); fi && \
    git checkout $DASH_GIT_TAG && \
    git submodule sync && git submodule update --init --force --recursive

RUN cd dash/depends && \
    make -j$(nproc)

RUN cd dash && \
    ./autogen.sh && \
    ./configure --prefix=$PWD/depends/x86_64-pc-linux-gnu && \
    make -j$(nproc)

# ---

# runtime stage
FROM ubuntu:20.04

COPY --from=0 /src/dash/src/dash-cli \
              /src/dash/src/dash-tx \
              /src/dash/src/dash-wallet \
              /src/dash/src/dashd \
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

RUN groupadd -r dash -g 1000 && \
    adduser --uid 1000 --gid 1000 --system --disabled-password dash && \
	mkdir -p /home/dash/.dashcore && \
	chown -R dash:dash /home/dash/.dashcore

USER dash
WORKDIR /home/dash
ENV TZ="UTC"

ENV http_proxy=socks5h://10.1.0.2:9050
ENV https_proxy=socks5h://10.1.0.2:9050

EXPOSE 9999 9998
VOLUME /home/dash/.dashcore

ADD entrypoint.sh /
