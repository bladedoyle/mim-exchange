
WALLET_PASS=foo

docker exec -it zcash zcashd-wallet-tool -rpcuser=foo -rpcpassword=$WALLET_PASS -rpcconnect=10.1.0.14 -rpcport=8232
docker exec -it zcash zcash-cli -rpcuser=foo -rpcpassword=foo -rpcconnect=10.1.0.14 -rpcport=8232 z_getnewaccount
