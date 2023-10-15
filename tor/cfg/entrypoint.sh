#!/bin/sh -e

# https://github.com/flungo-docker/tor-router

# Configure environment variables
TOR_ROUTER_USER="tor-router"
TOR_ROUTER_HOME="/opt/tor-router"
TOR_CONFIG_FILE="${TOR_ROUTER_HOME}/torrc"

set -x
echo 'Setting up container'

# Configure iptables
iptables-restore "${TOR_ROUTER_HOME}/iptables.rules"

# Run tor as the TOR_ROUTER_USER
echo 'Starting the Tor router'
exec sudo -u "${TOR_ROUTER_USER}" tor -f "${TOR_CONFIG_FILE}" "$@"
