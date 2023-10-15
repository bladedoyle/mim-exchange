# Multistage docker build, requires docker 17.05

# builder stage
FROM ubuntu:20.04 as builder
ARG TOR_GIT_TAG="latest"
ARG ADDRESSES="testnet"

RUN set -e && \
    apt-get update -q -y --no-install-recommends && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -q -y --no-install-recommends \
    ca-certificates \
    git build-essential automake libevent-dev libssl-dev zlib1g-dev


WORKDIR /src
RUN git clone https://git.torproject.org/tor.git && \
    cd tor && \
    if [ "x$TOR_GIT_TAG" = "xlatest" ]; then TOR_GIT_TAG=$(git describe --tags $(git rev-list --tags --max-count=1)); fi && \
    git checkout $TOR_GIT_TAG && \
    ./autogen.sh && \
    ./configure --disable-asciidoc && \
    make -j$(nproc)

# ---

# runtime stage
FROM ubuntu:20.04
ARG ADDRESSES="testnet"

COPY --from=0 /src/tor/src/app/tor /src/tor/src/tools/tor-resolve /src/tor/src/tools/tor-print-ed-signing-cert /src/tor/src/tools/tor-gencert \
                  /usr/local/bin/

RUN set -e && \
    apt-get update -q -y --no-install-recommends && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -q -y --no-install-recommends \
      ca-certificates \
      netcat \
      libevent-2.1-7 \
      tor iptables sudo \
      bind9-dnsutils curl telnet net-tools nmap \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt

ENV TZ="UTC"

RUN groupadd -r tor-router -g 9001 && \
    adduser --uid 9001 --gid 9001 --system --disabled-password tor-router


# Expose the ports made available through Tor
EXPOSE 80 8080 9050 5353/udp

# Populate the tor-router configurations
COPY cfg/entrypoint.sh /opt/tor-router/
COPY cfg/iptables.rules /opt/tor-router/
COPY cfg/torrc /opt/tor-router/
COPY cfg/www-${ADDRESSES} /opt/tor-router/www
COPY cfg/admin-${ADDRESSES} /opt/tor-router/admin

RUN chown -R tor-router.tor-router /opt/tor-router && \
    chmod -R 400 /opt/tor-router/torrc /opt/tor-router/www /opt/tor-router/admin && \
    chmod 700 /opt/tor-router/www  /opt/tor-router/admin /opt/tor-router/admin/authorized_clients
#   /opt/tor-router/www/authorized_clients

# Set the container's WORKDIR and ENTRYPOINT
WORKDIR /opt/tor-router
ENTRYPOINT ["/opt/tor-router/entrypoint.sh"]
