#!/bin/bash

if [ -z "$NODE_RPC_USER" ]; then
    echo "XXXXX: Can not start without environment set"
    sleep 10
    exit 1
fi

if [ "$NETWORK" == "testnet" ]; then
  rpcbind="0.0.0.0:7332"
  rpcallow="0.0.0.0/0"
  network="-testnet"
  rm -f /home/bitcoin/.bitcoin/testnet3/debug.log
  mkdir -p /home/bitcoin/.bitcoin/testnet3/
  ln -sf /dev/stdout /home/bitcoin/.bitcoin/testnet3/debug.log
else
  rpcbind="10.1.0.12:7332"
  rpcallow="10.1.0.0/24"
  network=""
  rm -f /home/bitcoin/.bitcoin/debug.log
  ln -sf /dev/stdout /home/bitcoin/.bitcoin/debug.log
fi

if [ "$REINDEX" == "true" ]; then
  reindex="-reindex"
fi


exec /usr/local/bin/bitcoind \
  $network \
  $reindex \
  -server \
  -printtoconsole \
  -proxy=10.0.0.2:9050 \
  -prune=2048 \
  -rpcbind=$rpcbind \
  -rpcuser=$NODE_RPC_USER \
  -rpcpassword=$NODE_RPC_PASS \
  -rpcallowip=$rpcallow
