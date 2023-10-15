FROM nginx:latest

RUN set -e && \
    apt-get update -q -y --no-install-recommends && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -q -y --no-install-recommends \
      ca-certificates \
      nginx \
      uwsgi-plugin-python3 \
      python3 \
      python3-pip \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt

ENV TZ="UTC"

COPY nginx.conf /etc/nginx/

EXPOSE 80
