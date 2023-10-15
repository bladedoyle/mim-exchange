Create BTC Wallet so it loads on start:
  bitcoin-cli -rpcuser=$BITCOIND_RPC_USER -rpcpassword=$BITCOIND_RPC_PASS createwallet "wallet" false false $BITCOIN_WALLET_PASS true true true

Litecoin wallet passphrase is provided in get_wallet() method

watch "dash-cli --testnet --rpcport=9998 --rpcuser=foo --rpcpassword=foo getbalances

 w

zcashd-wallet-tool --testnet --rpcport 8232 --rpcuser foo --rpcpassword foo --rpcclienttimeout 0



wownero wallet seed:

The recovery phrase is:

anxiety total shocking kept duets building erosion lesson
push sidekick hawk iguana dwindling sober oyster tattoo
frown adult adopt because palace diode boxes cafe sidekick



transpartent 64x64 logo:

mogrify -strip btc_icon_64.png
mogrify -strip xmr_icon.64.png
mogrify -strip ltc_logo_64.png
mogrify -strip zec_icon_64.png
mogrify -strip dash_icon_64.png
mogrify -strip doge_icon_64.png
mogrify -strip wownero_icon_64.png

import base64
with open("xmr_icon.64.png", "rb") as fh:
    bytes = fh.read()
    print(base64.b64encode(bytes).decode())


forms.py line 85 "testnet"

wallet rpc passwords in lib/addresses.py, lib/wallets.py

fix tor sends for monero (try on mainnnet)

configs:
price data expire time 10 minutes in price_oracle.py line 104
exchange rate data expires in 30 minutes in swap.py line 76
exchange fee lib/exchange.py
swap cookie expire time app.py line 163
minimum swap value forms.py line 60
expire_afer = timedelta(days=7) mime.py
delete_after = timedelta(days=7) mime.py
target_balance_ratio =   in liquidity_mgr.py
			"btc": 1.0,
            "xmr": 0.8,
wallet username and password



CMC api key is in my name: price_oracle.py

curl https://altquick.com/api/v1/ticker/price
{"market":"BTC_WOW","price":"0.0000018"}

----

Does this mean there was a chain reorg and the transaction was reversed?

bitcoind         | 2023-01-23T19:49:22Z UpdateTip: new best=0000000000000008d6320e0e235c3429e6a8342422e4c44790cfb872c1d6d226 height=2417571 version=0x20000004 log2_work=75.129245 tx=64790666 date='2023-01-23T19:49:08Z' progress=1.000000 cache=1.5MiB(10715txo)
bitcoind         | 2023-01-23T19:49:22Z [wallet] AddToWallet 3fb87f625d60c94d121d5bee77eb9268f310600f1757bd8f5680aa6f07fd3d2d  update

Why wasnt this tx put into the replacment block or some block soon after that?
---

get_exchange_heartbeat



ProtonMail:
mimexchange@proton.me
05ff22af7dc6
https://mail.protonmailrmez3lotccipshtkleegetolb73fuirgj7r4o4vfu7ozyd.onion/u/0/inbox?welcome=true

Discord:
mimexchange@proton.me
f9d1c5fec9d7


7BEP74G2moX15qPKqQGHhcKsnpDAp87n5X23uiz6wuRmVMfstfpbvxaL5bUNaQNruyEwd1A4sUqnFg4GqQiVzRtGTzPKCfq
tb1qjv3023canpmnn89mflfwq9ywzyyd3z3ws6aye0   
bchtest:qpmxeatf3dfuypj6g3ll6g7f9szyjfmwdq0ajfjcy4

dash: yVGJA75hNwmyFXTMErgdv4F85C7FUryWQE

75d18437e941 

-----

Exchange Data Flow

1. User input 
    quoted_swap_from_amount
    swap_from
    swap_to

2. Exchange calculates estimate
    id
    ts
    quoted_swap_to_amount
    quoted_swap_expire_ts

-- First write to DB

3. User input
    swap_to_address

4. Exchange generates
    swap_from_address

-- mime exchange 

5. User sends from coins, one confirmation
    recvd_from = True
    swap_from_amount
    swap_to_amount
    exchange_rate
    swap_executed_ts

6. Exchange sends to coins
    sent_to_txid

7. one confirmation
    sent_to_confirmed = True

---------------------

Possible States:

##
# Active swaps

* Incomplete and Expired
  - delete the swap
  - continue

* Payment Received but exchange not calculated
  - calculate exchange 
* Payment Received and exchange calculated but not sent
  - send swap
* Payment Received and exchange sent but not confirmed
  - check for send tx confirmation
* Payment Received and exchange confirmed - Completed
  - move swap to completed
  - continue


* Error sending and no refund address provided
  - continue
* Error sending and refund address provided but no refund sent 
  - send refund
* Error sending and Refund sent but not confirmed
  - check for refund tx confirmation
* Error sending and Refund Confirmed - Completed
  - move swap to completed 
  - continue

##
# Completed swaps

* Swap completed and Extra TX received but not refunded
* Swap completed and extra tx received but not refunded and no refund address provided
* swap completed and extra tx received but not refunded and refund address provided
* swap completed and extra tx received and refunded but not confirmed
* swap completed and extra tx received and refund tx confirmed



---------------------

zcash-cli --testnet --rpcport=8232 --rpcuser=foo --rpcpassword=foo getbalance
dash-cli --testnet --rpcport=9998 --rpcuser=foo --rpcpassword=foo getbalances


ltc address: tltc1q54h36eykleulhfxr3paq9k80fkys77k9z5gdk0


            # https://zcash-rpc.github.io/z_getoperationstatus.html
            status = []
            while "status" not in status:
                status = wallet.z_getoperationresult([opid])
            # https://zcash-rpc.github.io/z_getoperationresult.html
            status = []
            while len(result) == 0:
                result = wallet.z_getoperationresult([opid])
            return result["txid"]



1984
mimexchange@proton.me
dcD01.13_b4Cf41-5