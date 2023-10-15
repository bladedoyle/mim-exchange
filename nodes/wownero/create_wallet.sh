WALLET_PASS=foo

docker stop wownero-wallet
docker run -it --rm -v wownero_wallet:/home/wownero/.wownero:rw -u wownero --entrypoint /bin/bash wownero -c "/usr/local/bin/wownero-wallet-cli --password $WALLET_PASS --stagenet --generate-new-wallet /home/wownero/.wownero/wallet"
docker start wownero-wallet
