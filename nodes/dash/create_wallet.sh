#!/bin/bash

DASH_RPC_USER=foo
DASH_RPC_PASS=foo
DASH_WALLET_PASS=foo

docker exec -it dash dash-cli -rpcuser=$DASH_RPC_USER -rpcpassword=$DASH_RPC_PASS -rpcconnect=10.1.0.15 createwallet "wallet" false false $DASH_WALLET_PASS true true 
