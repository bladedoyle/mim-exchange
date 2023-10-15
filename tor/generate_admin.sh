#!/bin/bash

# Admin Hidden Service 
# Generate keys and address
# For testnet and mainnet

# Generate client auth keys
# testnet
rm -rf admin_keys_testnet
mkdir -p admin_keys_testnet
# Generate the key
openssl genpkey -algorithm x25519 -out admin_keys_testnet/k1.prv.pem
# Base 32 public and private keys
cat admin_keys_testnet/k1.prv.pem | grep -v " PRIVATE KEY" | base64pem -d | tail --bytes=32 | base32 | sed 's/=//g' > admin_keys_testnet/k1.prv.key
openssl pkey -in admin_keys_testnet/k1.prv.pem -pubout | grep -v " PUBLIC KEY" | base64pem -d | tail --bytes=32 | base32 | sed 's/=//g' > admin_keys_testnet/k1.pub.key
# Create the hidden service authorized_clients file
echo "descriptor:x25519:$(cat admin_keys_testnet/k1.pub.key)" > admin_keys_testnet/admin.auth
# Put the keys in place
rm -rf cfg/admin-testnet
mkdir -p cfg/admin-testnet/authorized_clients
cp admin_keys_testnet/admin.auth cfg/admin-testnet/authorized_clients/admin.auth

# mainnet
rm -rf admin_keys_mainnet
mkdir -p admin_keys_mainnet
# Generate the key
openssl genpkey -algorithm x25519 -out admin_keys_mainnet/k1.prv.pem
# Base 32 public and private keys
cat admin_keys_mainnet/k1.prv.pem | grep -v " PRIVATE KEY" | base64pem -d | tail --bytes=32 | base32 | sed 's/=//g' > admin_keys_mainnet/k1.prv.key
openssl pkey -in admin_keys_mainnet/k1.prv.pem -pubout | grep -v " PUBLIC KEY" | base64pem -d | tail --bytes=32 | base32 | sed 's/=//g' > admin_keys_mainnet/k1.pub.key
# Create the hidden service authorized_clients file
echo "descriptor:x25519:$(cat admin_keys_mainnet/k1.pub.key)" > admin_keys_mainnet/admin.auth
# Put the keys in place
rm -rf cfg/admin-mainnet
mkdir -p cfg/admin-mainnet/authorized_clients
cp admin_keys_mainnet/admin.auth cfg/admin-mainnet/authorized_clients/admin.auth


# Generate admin service address
# testnet
rm -rf admin_address_testnet
mkdir -p admin_address_testnet
./mkp224o/mkp224o mimeadt -t 14 -v -n 1 -d admin_address_testnet
rm -f cfg/admin-testnet/hostname cfg/admin-testnet/hs_ed25519_public_key cfg/admin-testnet/hs_ed25519_secret_key
mkdir -p cfg/admin-testnet
mv admin_address_testnet/*/* cfg/admin-testnet
# mainnet
rm -rf admin_address_mainnet
mkdir -p admin_address_mainnet
./mkp224o/mkp224o mimeadm -t 14 -v -n 1 -d admin_address_mainnet
mkdir -p cfg/admin-mainnet
mv admin_address_mainnet/*/* cfg/admin-mainnet
