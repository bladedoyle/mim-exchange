#!/bin/bash

if [ -z "$NODE_RPC_USER" ]; then
    echo "XXXXX: Can not start without environment set"
    sleep 10
    exit 1
fi

if [ "$NETWORK" == "testnet" ]; then
  rpcbind="0.0.0.0:22555"
  rpcallow="0.0.0.0/0"
  network="-testnet"
  rm -f /home/dogecoin/.dogecoin/testnet3/debug.log
  mkdir -p /home/dogecoin/.dogecoin/testnet3/
  ln -sf /dev/stdout /home/dogecoin/.dogecoin/testnet3/debug.log
else
  rpcbind="10.1.0.17:22555"
  rpcallow="10.1.0.0/24"
  network=""
  rm -f /home/dogecoin/.dogecoin/debug.log
  ln -sf /dev/stdout /home/dogecoin/.dogecoin/debug.log
fi

if [ "$REINDEX" == "true" ]; then
  reindex="-reindex"
fi


exec /usr/local/bin/dogecoind \
  $network \
  $reindex \
  -server \
  -printtoconsole \
  -shrinkdebugfile=0 \
  -proxy=10.0.0.2:9050 \
  -prune=3072 \
  -rpcbind=$rpcbind \
  -rpcuser=$NODE_RPC_USER \
  -rpcpassword=$NODE_RPC_PASS \
  -rpcallowip=$rpcallow
