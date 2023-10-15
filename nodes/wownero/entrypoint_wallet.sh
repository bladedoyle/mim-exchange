#!/bin/bash

if [ "$NETWORK" == "testnet" ]; then
  rpcbindip="0.0.0.0"
  network="--stagenet"
  walletfile="/home/wownero/.wownero/wallet"
else
  rpcbindip="10.1.0.18"
  network=""
  walletfile="/home/wownero/.wownero/wallet"
fi


/usr/local/bin/wownero-wallet-rpc \
  $network \
  --wallet-file=$walletfile \
  --password=$WALLET_PASS \
  --rpc-bind-ip=$rpcbindip \
  --rpc-bind-port=34566 \
  --confirm-external-bind \
  --rpc-login=$NODE_RPC_USER:$NODE_RPC_PASS \
  --daemon-host=10.1.0.16 \
  --daemon-port=34568 \
  --trusted-daemon \
  --daemon-login=$NODE_RPC_USER:$NODE_RPC_PASS \
  --non-interactive

exit $?
