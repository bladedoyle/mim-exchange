#!/bin/bash

if [ -z "$NODE_RPC_USER" ]; then
    echo "XXXXX: Can not start without environment set"
    sleep 10
    exit 1
fi

if [ "$NETWORK" == "testnet" ]; then
  rpcbindip="0.0.0.0"
  network="--stagenet"
else
  rpcbindip="10.1.0.16"
  network=""
fi


exec /usr/local/bin/wownerod \
  $network \
  --disable-dns-checkpoints \
  --enable-dns-blocklist \
  --out-peers=96 \
  --in-peers=32 \
  --non-interactive \
  --p2p-bind-ip=0.0.0.0 \
  --rpc-bind-port=34568 \
  --rpc-bind-ip=$rpcbindip \
  --rpc-login=$NODE_RPC_USER:$NODE_RPC_PASS \
  --confirm-external-bind \
  --log-level=0 \
  --prune-blockchain \
  --fast-block-sync=1
