#!/bin/bash

LITECOIND_RPC_USER=foo
LITECOIND_RPC_PASS=foo
LITECOIN_WALLET_PASS=foo

docker exec -it litecoind litecoin-cli -rpcuser=$LITECOIND_RPC_USER -rpcpassword=$LITECOIND_RPC_PASS -rpcconnect=10.1.0.13 createwallet "wallet" false false $LITECOIN_WALLET_PASS true false true
