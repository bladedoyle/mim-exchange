# Sample Testnet Exchange

Website: [http://mimexxxic7flxfu4bnin7q24eftztpxbox73zjkhb36a2qgvvaxhljid.onion/](http://mimexxxic7flxfu4bnin7q24eftztpxbox73zjkhb36a2qgvvaxhljid.onion/)

## Deploy Instructions

1. Create an Ubuntu 22.04 virtual machine (VM).
   - Minimum requirements for running all 8 blockchain nodes:
     - 12GB memory
     - 8 CPU cores
     - 100GB disk (SSD preferred)
2. Install Docker and Docker Compose.
3. Install libraries and tools for Tor vanity addresses:
   ```
   sudo apt-get install libsodium-dev basez
   ```
4. Clone this git project and subproject(s).
   ```
   git clone https://github.com/bladedoyle/mim-exchange.git
   cd mim-exchange
   git submodule update --init --recursive
   ```
5. Run the following commands:
    ```
    make -j4 -C tor/mkp224o/
    ./tor/generate_admin.sh
    ./tor/generate_exchange.sh
    ```
6. Your exchange onion address is found here:
   ```
    cat tor/cfg/www-testnet/hostname
   ```
7. Edit .env and set: NETWORK=testnet.
8. Build Docker Compose containers (this will take a long time):
   ```
    docker-compose build
   ```
9. If it fails due to memory issues, run the command again until it succeeds.
10. Start the containers in detached mode (this will take a long time for all nodes to sync pruned blockchains):
    ```
    docker-compose up -d
    ```
11. Create wallets for the nodes:
    Some nodes automatically create a wallet, while others do not.
    Wallet creation is not yet fully automated, but scripts are available to help. For example:
    ```
    find . -type f | grep create_wallet
    ./nodes/monero/create_wallet.sh
    ./nodes/zcash/create_wallet.sh
    ...
    ```
12. View all logs in real-time:
    ```
    docker-compose logs -f
    ```
13. Open the Tor browser and go to your exchange onion address.

## Donations
More Donations == More Coffee == More Code

XMR: 43i7q6hVrMdgY21RH7nMghSPA6s5jjGXDeEmLjL3pNFfD1XBYqf6hJpWVabfGJ5ydJKdaBjKdFvMe1kaKRj5w7Ao7q7mK8v
