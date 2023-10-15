FROM ubuntu:20.04 as builder
ARG ZCASH_GIT_TAG="latest"

# Install dependencies - https://zcash.readthedocs.io/en/latest/rtd_pages/Debian-Ubuntu-build.html
RUN set -e && \
    apt-get update -q -y --no-install-recommends && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -q -y --no-install-recommends \
      ca-certificates \
      autoconf \
      automake \
      bsdmainutils \
      build-essential \
      curl \
      g++-multilib \
      git \
      libc6-dev \
      libtool \
      m4 \
      ncurses-dev \
      pkg-config \
      python3 \
      python3-zmq \
      unzip \
      wget \
      zlib1g-dev

WORKDIR /src
RUN git clone https://github.com/zcash/zcash.git && \
    cd zcash && \
    if [ "x$ZCASH_GIT_TAG" = "xlatest" ]; then ZCASH_GIT_TAG=$(git describe --tags $(git rev-list --tags --max-count=1)); fi && \
    git checkout $ZCASH_GIT_TAG && \
    git submodule sync && git submodule update --init --force --recursive && \
    ./zcutil/fetch-params.sh

RUN cd zcash && \
    ./zcutil/build.sh -j$(nproc)


# ---

# runtime stage
FROM ubuntu:20.04

COPY --from=0 /src/zcash/src/zcashd-wallet-tool \
              /src/zcash/src/zcash-tx \
              /src/zcash/src/zcash-inspect \
              /src/zcash/src/zcash-cli \
              /src/zcash/src/zcashd \
              /src/zcash/src/zcash-gtest \
              /src/zcash/zcutil/fetch-params.sh \
                  /usr/local/bin/

ENV TZ="UTC"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN set -e && \
    apt-get update -q -y --no-install-recommends && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -q -y --no-install-recommends \
      ca-certificates \
      netcat \
      curl \
      libevent-pthreads-2.1-7 \
      libevent-2.1-7 \
      libsqlite3-0 \
      libzmq5 \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt

RUN groupadd -r zcash -g 1000 && \
    adduser --uid 1000 --gid 1000 --system --disabled-password zcash && \
    mkdir -p /home/zcash/.zcash && \
    chown -R zcash:zcash /home/zcash/.zcash

USER zcash
WORKDIR /home/zcash

RUN touch /home/zcash/.zcash/zcash.conf && \
    bash /usr/local/bin/fetch-params.sh

ENV http_proxy=socks5h://10.1.0.2:9050
ENV https_proxy=socks5h://10.1.0.2:9050

EXPOSE 8232
EXPOSE 8233

VOLUME /home/zcash/.zcash

ADD entrypoint.sh /
