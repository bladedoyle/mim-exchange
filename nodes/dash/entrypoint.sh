#!/bin/bash

if [ -z "$NODE_RPC_USER" ]; then
    echo "XXXXX: Can not start without environment set"
    sleep 10
    exit 1
fi

if [ "$NETWORK" == "testnet" ]; then
  rpcbind="0.0.0.0:9998"
  rpcallow="0.0.0.0/0"
  network="-testnet"
else
  rpcbind="10.1.0.15:9998"
  rpcallow="10.1.0.0/24"
  network=""
fi

if [ "$REINDEX" == "true" ]; then
  reindex="-reindex"
fi


exec /usr/local/bin/dashd \
  $network \
  $reindex \
  -server \
  -printtoconsole \
  -nodebuglogfile \
  -proxy=10.0.0.2:9050 \
  -prune=2048 \
  -rpcbind=$rpcbind \
  -rpcuser=$NODE_RPC_USER \
  -rpcpassword=$NODE_RPC_PASS \
  -rpcallowip=$rpcallow
