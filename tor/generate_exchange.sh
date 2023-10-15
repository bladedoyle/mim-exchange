#!/bin/bash

VANITY_STRING=mime

# testnet
rm -rf tmp
mkdir tmp
./mkp224o/mkp224o $VANITY_STRING -t 14 -v -n 1 -d tmp
rm -rf cfg/www-testnet
mkdir -p cfg/www-testnet
mv tmp/*/* cfg/www-testnet
rm -rf tmp

# mainnet
# Generate www client auth keys
rm -rf www_keys_mainnet
mkdir -p www_keys_mainnet
# Generate the key
openssl genpkey -algorithm x25519 -out www_keys_mainnet/k1.prv.pem
# Base 32 public and private keys
cat www_keys_mainnet/k1.prv.pem | grep -v " PRIVATE KEY" | base64pem -d | tail --bytes=32 | base32 | sed 's/=//g' > www_keys_mainnet/k1.prv.key
openssl pkey -in www_keys_mainnet/k1.prv.pem -pubout | grep -v " PUBLIC KEY" | base64pem -d | tail --bytes=32 | base32 | sed 's/=//g' > www_keys_mainnet/k1.pub.key
# Create the hidden service authorized_clients file
echo "descriptor:x25519:$(cat www_keys_mainnet/k1.pub.key)" > www_keys_mainnet/www.auth
# Put the keys in place
rm -rf cfg/www-mainnet
mkdir -p cfg/www-mainnet/authorized_clients
cp www_keys_mainnet/www.auth cfg/www-mainnet/authorized_clients/www.auth


# Generate exchange service address
rm -rf tmp
mkdir tmp
./mkp224o/mkp224o $VANITY_STRING -t 14 -v -n 1 -d tmp
mv tmp/*/* cfg/www-mainnet
rm -rf tmp
