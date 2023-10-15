FROM ubuntu:20.04
ARG BITCOINCASH_VERSION=26.0.0


RUN set -e && \
    apt-get update -q -y --no-install-recommends && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -q -y --no-install-recommends \
      ca-certificates \
      gnupg \
      netcat \
      curl \
      telnet \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt

ENV BITCOIN_SHA256 e32e05fd63161f6f1fe717fca789448d2ee48e2017d3d4c6686b4222fe69497e

RUN curl -SLO https://github.com/bitcoin-cash-node/bitcoin-cash-node/releases/download/v${BITCOINCASH_VERSION}/bitcoin-cash-node-${BITCOINCASH_VERSION}-x86_64-linux-gnu.tar.gz \
  && echo "${BITCOIN_SHA256} bitcoin-cash-node-${BITCOINCASH_VERSION}-x86_64-linux-gnu.tar.gz" | sha256sum -c - \
  && tar --strip=2 -xzf *.tar.gz -C /usr/local --strip-components=1 --exclude=*-qt \
  && rm *.tar.gz

RUN groupadd -r bitcoin -g 1000 && \
    adduser --uid 1000 --gid 1000 --system --disabled-password bitcoin && \
	mkdir -p /home/bitcoin/.bitcoin && \
	chown -R bitcoin:bitcoin /home/bitcoin/.bitcoin

USER bitcoin
WORKDIR /home/bitcoin
ENV TZ="UTC"

ENV http_proxy=socks5h://10.1.0.2:9050
ENV https_proxy=socks5h://10.1.0.2:9050

EXPOSE 8332 8333 18332 18333
VOLUME /home/bitcoin/.bitcoin

ADD entrypoint.sh /
