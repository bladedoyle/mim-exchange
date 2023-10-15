#!/bin/bash

if [ -z "$NODE_RPC_USER" ]; then
    echo "XXXXX: Can not start without environment set"
    sleep 10
    exit 1
fi

if [ "$NETWORK" == "testnet" ]; then
  rpcbind="0.0.0.0:8232"
  rpcallow="0.0.0.0/0"
  network="-testnet"
  exportdir="/home/zcash/.zcash/testnet3/wallet_export"
else
  rpcbind="10.1.0.14:8232"
  rpcallow="10.1.0.0/24"
  network=""
  exportdir="/home/zcash/.zcash/wallet_export"
fi

if [ "$REINDEX" == "true" ]; then
  reindex="-reindex"
fi

mkdir -p /home/zcash/.zcash/wallet_export

exec /usr/local/bin/zcashd \
  $network \
  $reindex \
  -server=1 \
  -exportdir=$exportdir \
  -debuglogfile=/dev/stdout \
  -proxy=10.0.0.2:9050 \
  -prune=2048 \
  -rpcbind=$rpcbind \
  -rpcuser=$NODE_RPC_USER \
  -rpcpassword=$NODE_RPC_PASS \
  -rpcallowip=$rpcallow
