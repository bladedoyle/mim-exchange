MONERO_WALLET_PASS=foo

docker stop monero_wallet
docker run -it --rm -v monero_wallet-testnet:/home/monero/.bitmonero:rw --entrypoint /bin/bash monero -c "mkdir -p /home/monero/.bitmonero/stagenet && /usr/local/bin/monero-wallet-cli --stagenet --password $MONERO_WALLET_PASS --generate-new-wallet /home/monero/.bitmonero/stagenet/wallet"
docker start monero_wallet
