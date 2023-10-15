#!/bin/bash

if [ "$NETWORK" == "testnet" ]; then
  rpcbindip="0.0.0.0"
  network="--stagenet"
  walletfile="/home/monero/.bitmonero/stagenet/wallet"
else
  rpcbindip="10.1.0.5"
  network=""
  walletfile="/home/monero/.bitmonero/wallet"
fi


/usr/local/bin/monero-wallet-rpc \
  $network \
  --wallet-file=$walletfile \
  --password=$WALLET_PASS \
  --rpc-bind-ip=$rpcbindip \
  --rpc-bind-port=18082 \
  --confirm-external-bind \
  --rpc-login=$NODE_RPC_USER:$NODE_RPC_PASS \
  --daemon-host=10.1.0.3 \
  --daemon-port=38081 \
  --trusted-daemon \
  --daemon-login=$NODE_RPC_USER:$NODE_RPC_PASS \
  --non-interactive

exit $?
