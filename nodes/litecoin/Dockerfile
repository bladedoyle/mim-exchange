FROM ubuntu:20.04
ARG LITECOIN_VERSION=0.21.2.1


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

RUN for key in \
    # Litecoin (davidburkett38’s key)
    3620E9D387E55666 \
    ; do \
    gpg --no-tty --keyserver pgp.mit.edu --recv-keys "$key" || \
    gpg --no-tty --keyserver keyserver.pgp.com --recv-keys "$key" || \
    gpg --no-tty --keyserver ha.pool.sks-keyservers.net --recv-keys "$key" || \
    gpg --no-tty --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys "$key" ; \
  done

RUN curl -SLO https://download.litecoin.org/litecoin-${LITECOIN_VERSION}/linux/litecoin-${LITECOIN_VERSION}-x86_64-linux-gnu.tar.gz \
  && curl -SLO https://download.litecoin.org/litecoin-${LITECOIN_VERSION}/SHA256SUMS.asc \
  && gpg --verify SHA256SUMS.asc \
  && grep $(sha256sum litecoin-${LITECOIN_VERSION}-x86_64-linux-gnu.tar.gz | awk '{ print $1 }') SHA256SUMS.asc \
  && tar --strip=2 -xzf *.tar.gz -C /usr/local/bin \
  && rm *.tar.gz

RUN groupadd -r litecoin -g 1000 && \
    adduser --uid 1000 --gid 1000 --system --disabled-password litecoin && \
	mkdir -p /home/litecoin/.litecoin && \
	chown -R litecoin:litecoin /home/litecoin/.litecoin

USER litecoin
WORKDIR /home/litecoin
ENV TZ="UTC"

ENV http_proxy=socks5h://10.1.0.2:9050
ENV https_proxy=socks5h://10.1.0.2:9050

EXPOSE 9332 9333 19332 19333 19444
VOLUME /home/litecoin/.litecoin

ADD entrypoint.sh /
