# Multistage docker build, requires docker 17.05

# builder stage
FROM ubuntu:20.04 as builder
ARG WOWNERO_GIT_TAG="latest"

RUN set -e && \
    apt-get update -q -y --no-install-recommends && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -q -y --no-install-recommends \
        automake \
        autotools-dev \
        bsdmainutils \
        build-essential \
        ca-certificates \
        ccache \
        cmake \
        curl \
        git \
        libtool \
        pkg-config \
        gperf


WORKDIR /src
RUN git clone --recursive https://git.wownero.com/wownero/wownero.git && \
    cd wownero && \
    if [ "x$WOWNERO_GIT_TAG" = "xlatest" ]; then WOWNERO_GIT_TAG=$(git describe --tags $(git rev-list --tags --max-count=1)); fi && \
    git checkout $WOWNERO_GIT_TAG && \
    git submodule sync && git submodule update --init --force --recursive && \
    make -j$(nproc) depends target=$(contrib/depends/config.guess)

# ---

# runtime stage
FROM ubuntu:20.04

COPY --from=0 /src/wownero/build/*/release/bin /usr/local/bin/

RUN set -e && \
    apt-get update -q -y --no-install-recommends && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -q -y --no-install-recommends \
      ca-certificates \
      netcat bind9-dnsutils curl telnet net-tools nmap \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt

RUN groupadd -r wownero -g 1000 && \
    adduser --uid 1000 --gid 1000 --system --disabled-password wownero && \
	mkdir -p /home/wownero/.wownero && \
	chown -R wownero:wownero /home/wownero/.wownero

USER wownero
WORKDIR /home/wownero
ENV TZ="UTC"

ENV http_proxy=socks5h://10.1.0.2:9050
ENV https_proxy=socks5h://10.1.0.2:9050

EXPOSE 34566 34567 34568
VOLUME /home/wownero/.wownero

ADD entrypoint.sh /
ADD entrypoint_wallet.sh /
