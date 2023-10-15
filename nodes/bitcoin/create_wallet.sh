#!/bin/bash

BITCOIND_RPC_USER=foo
BITCOIND_RPC_PASS=foo
BITCOIN_WALLET_PASS=foo

docker exec -it bitcoind bitcoin-cli -rpcuser=$BITCOIND_RPC_USER -rpcpassword=$BITCOIND_RPC_PASS createwallet "wallet" false false $BITCOIN_WALLET_PASS true true true
