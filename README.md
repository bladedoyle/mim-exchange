# Sample Testnet Exchange

Website: [http://mimexxxic7flxfu4bnin7q24eftztpxbox73zjkhb36a2qgvvaxhljid.onion/](http://mimexxxic7flxfu4bnin7q24eftztpxbox73zjkhb36a2qgvvaxhljid.onion/)
Clearnet Proxy: [http://mimexchange.cc/](http://mimexchange.cc/)

## Deploy Instructions

1. Create an Ubuntu 22.04 virtual machine (VM).
   - Minimum requirements for running all 8 blockchain nodes:
     - 12GB memory
     - 8 CPU cores
     - 100GB disk (SSD preferred)
2. Install Docker and Docker Compose
   https://docs.docker.com/engine/install/ubuntu/
   ```
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```
4. Install libraries and tools for Tor vanity addresses:
   ```
   sudo apt-get install libsodium-dev basez autoconf
   ```
5. Clone this git project and subproject(s).
   ```
   git clone https://github.com/bladedoyle/mim-exchange.git
   cd mim-exchange
   git submodule update --init --recursive
   ```
6. Run the following commands:
    ```
    cd tor/mkp224o
    ./autogen.sh
    ./configure
    make -j4
    cd ..
    ./generate_admin.sh
    ./generate_exchange.sh
    ```
7. Your exchange onion address is found here:
   ```
    cat tor/cfg/www-testnet/hostname
   ```
8. Edit .env and set: NETWORK=testnet.
9. Build Docker Compose containers (this will take a long time):
   ```
    docker-compose build
   ```
10. If it fails due to memory issues, add a swap file and run the docker-compose build command again
   ```
    sudo dd if=/dev/zero of=/swapfile2 bs=1G count=8
    chmod 0600 /swapfile2
    sudo mkswap /swapfile2
    sudo swapon /swapfile2
   ```
   And remove the extra swap after building
   ```
    sudo swapoff /swapfile2
    sudo rm /swapfile2
   ```
11. Start the containers in detached mode (this will take a long time for all nodes to sync pruned blockchains):
    ```
    docker-compose up -d
    ```
12. Create wallets for the nodes:
    Some nodes automatically create a wallet, while others do not.
    Wallet creation is not yet fully automated, but scripts are available to help. For example:
    ```
    find . -type f | grep create_wallet
    ./nodes/monero/create_wallet.sh
    ./nodes/zcash/create_wallet.sh
    ...
    ```
13. View all logs in real-time:
    ```
    docker-compose logs -f
    ```
14. Open the Tor browser and go to your exchange onion address.

## Donations
More Donations == More Coffee == More Code

XMR: 43MgMFmpmPmHUG1RFyDr5wZH3FpTbaiHSJUUGMAosG639p3L1uV1et2C6SBKjuV8QpE9Dcb5fK3GiWcR5bDfvkqWM6kkmij
