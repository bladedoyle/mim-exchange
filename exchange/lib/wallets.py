import os
from decimal import Decimal

# Wallet rpc
# btc / ltc / bch:
#   https://python-bitcoinlib.readthedocs.io/en/latest/
#   https://developer.bitcoin.org/reference/rpc/index.html
#   dash: https://dashcore.readme.io/docs/core-api-ref-remote-procedure-calls-wallet
from bitcoinrpc.authproxy import AuthServiceProxy as BtcAuthServiceProxy
from bitcoinrpc.authproxy import JSONRPCException as BtcJSONRPCException
# xmr:
#   https://github.com/monero-ecosystem/python-monerorpc
#   https://www.getmonero.org/resources/developer-guides/daemon-rpc.html
from monerorpc.authproxy import AuthServiceProxy as XmrAuthServiceProxy
from monerorpc.authproxy import JSONRPCException as XmrJSONRPCException


# Define our exceptions
class WalletEx(Exception):
    pass


def get_wallet(coin):
    RPC_USER = os.getenv('NODE_RPC_USER')
    RPC_PASS = os.getenv('NODE_RPC_PASS')
    if coin == "btc":
        try:
            rpc = BtcAuthServiceProxy("http://%s:%s@bitcoind:8332"%(RPC_USER, RPC_PASS))
            rpc.ping()
            rpc.walletpassphrase(RPC_PASS, 100000000)
            return rpc
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin == "ltc":
        try:
            rpc = BtcAuthServiceProxy("http://%s:%s@litecoind:9332"%(RPC_USER, RPC_PASS))
            rpc.ping()
            rpc.walletpassphrase(RPC_PASS, 100000000)
            return rpc
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin == "bch":
        try:
            rpc = BtcAuthServiceProxy("http://%s:%s@bitcoincash:7332"%(RPC_USER, RPC_PASS))
            rpc.ping()
            return rpc
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin == "zec":
        try:
            rpc = BtcAuthServiceProxy("http://%s:%s@zcash:8232"%(RPC_USER, RPC_PASS))
            rpc.ping()
            return rpc
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin == "dash":
        try:
            rpc = BtcAuthServiceProxy("http://%s:%s@dash:9998"%(RPC_USER, RPC_PASS))
            rpc.ping()
            rpc.walletpassphrase(RPC_PASS, 100000000)
            return rpc
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin == "doge":
        try:
            rpc = BtcAuthServiceProxy("http://%s:%s@dogecoin:22555"%(RPC_USER, RPC_PASS))
            rpc.ping()
            return rpc
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin == "xmr":
        try:
            wallet = XmrAuthServiceProxy("http://%s:%s@monero_wallet:18082/json_rpc"%(RPC_USER, RPC_PASS))
            return wallet
        except XmrJSONRPCException as e:
            raise WalletEx(e)
    elif coin == "wow":
        try:
            wallet = XmrAuthServiceProxy("http://%s:%s@wownero_wallet:34566/json_rpc"%(RPC_USER, RPC_PASS))
            return wallet
        except XmrJSONRPCException as e:
            raise WalletEx(e)
    else:
        raise WalletEx("Unsupported coin: {} in lib.wallets.get_wallet()".format(coin))


def get_daemon(coin):
    if coin in ["btc", "ltc", "bch", "zec", 'dash', 'doge']:
        return get_wallet(coin)
    elif coin == "xmr":
        RPC_USER = os.getenv('NODE_RPC_USER')
        RPC_PASS = os.getenv('NODE_RPC_PASS')
        try:
            daemon = XmrAuthServiceProxy(service_url="http://%s:%s@monerod:38081/json_rpc"%(RPC_USER, RPC_PASS))
            return daemon
        except XmrJSONRPCException as e:
            raise WalletEx(e)
    elif coin == "wow":
        RPC_USER = os.getenv('NODE_RPC_USER')
        RPC_PASS = os.getenv('NODE_RPC_PASS')
        try:
            daemon = XmrAuthServiceProxy(service_url="http://%s:%s@wownero:34568/json_rpc"%(RPC_USER, RPC_PASS))
            return daemon
        except XmrJSONRPCException as e:
            raise WalletEx(e) 
    else:
        raise WalletEx("Unsupported coin: {} in lib.wallets.get_daemon()".format(coin))

def wallet_balance(coin):
    wallet = get_wallet(coin)
    if coin in ["xmr", "wow"]:
        if coin == "xmr":
            atomic_units = Decimal("1e12")
        elif coin == "wow":
            atomic_units = Decimal("1e11")
        result = wallet.get_balance({"account_index": 0})
        balance = Decimal(result["balance"])/atomic_units
        unlocked = Decimal(result["unlocked_balance"])/atomic_units
        return {
                    "total": str(balance),
                    "available": str(unlocked),
            }
    elif coin == "btc":
        result = wallet.getbalances()["mine"]
        trusted = result["trusted"]
        pending = result["untrusted_pending"]
        immature = result["immature"]
        used = Decimal(0)
        if "used" in result:
            used = result["used"]
        return {
                    "total": str(trusted + pending + immature + used),
                    "available": str(trusted + used),
            }
    elif coin in ["doge", "zec"]:
        # https://zcash-rpc.github.io/getbalance.html
        # https://en.bitcoin.it/wiki/Original_Bitcoin_client/API_calls_list
        result = wallet.getbalance()
        return {
                    "total": str(result),
                    "available": str(result),
            }
    elif coin == "ltc":
        result = wallet.getbalances()["mine"]
        trusted = result["trusted"]
        pending = result["untrusted_pending"]
        immature = result["immature"]
        used = result["used"]
        return {
                    "total": str(trusted + pending + immature + used),
                    "available": str(trusted + used),
            }
    elif coin == "bch":
        result = wallet.getwalletinfo()
        confirmed = result["balance"]
        pending = result["unconfirmed_balance"]
        immature = result["immature_balance"]
        return {
                    "total": str(confirmed + pending + immature),
                    "available": str(confirmed),
            }
    elif coin == "dash":
        result = wallet.getbalances()["mine"]
        confirmed = result["trusted"]
        pending = result["untrusted_pending"]
        immature = result["immature"]
        used = result["used"]
        return {
                    "total": str(confirmed + pending + immature + used),
                    "available": str(confirmed + used),
            }
    else:
        raise WalletEx("Unsupported coin: {} in lib.wallets.wallet_balance()".format(coin))


def health(coin):
    wallet = get_wallet(coin)
    daemon = get_daemon(coin)
    if coin in ["btc", "ltc", "bch", "doge", "dash", "zec"]:
        info = daemon.getblockchaininfo()
        if info["verificationprogress"] < 0.9999:
            raise WalletEx("Node is out of sync")
        if info["headers"] == 0 or info["blocks"] == 0:
            raise WalletEx("Node is out of sync")
        if abs(info["headers"] - info["blocks"]) > 5:
            raise WalletEx("Node is syncing")
        balance = wallet_balance(coin)
    elif coin in ["xmr", "wow"]:
        wallet_height = wallet.get_height()
        daemon_info = daemon.get_info()
        if abs(wallet_height["height"] - daemon_info["height"]) > 2:
            raise WalletEx("Node or wallet is out of sync: {}: {} vs {}".format(coin, wallet_height["height"], daemon_info["height"]))
        # XXX TODO add daemon.sync_info()


# Get a list of receive txid for an address
def get_recv_tx_list(coin, address):
    wallet = get_wallet(coin)
    if coin in ["btc", "ltc", "bch"]:
        try:
            result = wallet.listreceivedbyaddress(1, False, False, address)
            if len(result) > 0:
                result = result[0]['txids']
            return result
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin == "dash":
        try:
            result = wallet.listreceivedbyaddress(1, False, False, False, address)
            if len(result) > 0:
                result = result[0]['txids']
            return result
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin == "doge":
        try:
            # https://en.bitcoin.it/wiki/Original_Bitcoin_client/API_calls_list
            result = wallet.listreceivedbyaddress(1, False, False)
            for recvd in result:
                if recvd["address"] == address:
                    return recvd["txids"]
            return []
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin == "zec":
        try:
            # https://zcash.github.io/rpc/z_listreceivedbyaddress.html
            result = wallet.z_listreceivedbyaddress(address, 1)
            if len(result) > 0:
                result = [r["txid"] for r in result]
            return result
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin in ["xmr", "wow"]:
        try:
            args = {
                "address": address
            }
            result = wallet.get_address_index(args)
            # https://www.getmonero.org/resources/developer-guides/wallet-rpc.html#incoming_transfers
            args = {
                "transfer_type": "all",
                "account_index": result["index"]["major"],
                "subaddr_indices": [result["index"]["minor"]]
            }
            result = wallet.incoming_transfers(args)
            if len(result) > 0:
                txids = [tx["tx_hash"] for tx in result["transfers"]]
            else:
                txids = []
            return txids
        except XmrJSONRPCException as e:
            raise WalletEx(e)
    else:
        raise WalletEx("Unsupported coin: {} in lib.wallets.get_recv_tx_list()".format(coin))

# Get recv tx data
def get_recv_tx(coin, txid):
    wallet = get_wallet(coin)
    if coin in ["btc", "ltc", "bch", "zec", "doge", "dash"]:
        try: 
            # https://developer.bitcoin.org/reference/rpc/gettransaction.html
            result = wallet.gettransaction(txid)
            if result["details"][0]["category"] != "receive":
                raise WalletEx(f"Not a receive transaction: {result}")
            return {
                "amount": result["amount"],
                "confirmations": result["confirmations"],
                "timereceived": result["timereceived"],
            }
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin in ["xmr", "wow"]:
        try:
            if coin == "xmr":
                atomic_units = Decimal("1e12")
            elif coin == "wow":
                atomic_units = Decimal("1e11")
            # https://www.getmonero.org/resources/developer-guides/wallet-rpc.html#get_transfer_by_txid
            args = {
                    "account_index": 0,
                    "txid": txid,
            }
            result = wallet.get_transfer_by_txid(args)
            if result["transfer"]["type"] not in ["in"]:
                raise WalletEx(f"Not a receive transaction: {result}")
            return {
                "amount": (result["transfer"]["amount"])/atomic_units,
                "confirmations": result["transfer"]["unlock_time"] or result["transfer"]["confirmations"],
                "timereceived": result["transfer"]["timestamp"],
            }
        except XmrJSONRPCException as e:
            raise WalletEx(e)
    else:
        raise WalletEx("Unsupported coin: {} in lib.wallets.get_recv_tx()".format(coin))


# Get send tx data
def get_send_tx(coin, txid):
    wallet = get_wallet(coin)
    if coin in ["btc", "ltc", "bch", "zec", "dash", "doge"]:
        try: 
            # https://developer.bitcoin.org/reference/rpc/gettransaction.html
            result = wallet.gettransaction(txid)
            if result["details"][0]["category"] != "send":
                raise WalletEx(f"Not a send transaction: {result}")
            return {
                "confirmations": result["confirmations"],
            }
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin in ["xmr", "wow"]:
        try:
            # https://www.getmonero.org/resources/developer-guides/wallet-rpc.html#get_transfer_by_txid
            args = {
                    "account_index": 0,
                    "txid": txid,
            }
            result = wallet.get_transfer_by_txid(args)
            if result["transfer"]["type"] not in ["out", "pending"]:
                raise WalletEx(f"Not a send transaction: {result}")
            return {
                "confirmations": result["transfer"].get("confirmations", 0),
            }
        except XmrJSONRPCException as e:
            raise WalletEx(e)
    else:
        raise WalletEx("Unsupported coin: {} in lib.wallets.get_send_tx()".format(coin))


# Returns true if a send transaction is confirmed on the blockchain
def send_tx_confirmed(coin, txid):
    return get_send_tx(coin, txid)["confirmations"] > 0

# Sends coins and returns txid
def send(coin, amount, address):
    wallet = get_wallet(coin)
    if coin in ["btc", "ltc", "bch"]:
        try:
            # https://developer.bitcoin.org/reference/rpc/sendtoaddress.html
            result = wallet.sendtoaddress(address, str(round(amount, 8)), "", "", True, True, 2, "unset", False)
            return result
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin == "dash":
        try:
            # https://dashcore.readme.io/docs/core-api-ref-remote-procedure-calls-wallet#sendtoaddress
            result = wallet.sendtoaddress(address, str(round(amount, 8)), "", "", True, True, False, 2, "UNSET", False)
            return result
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin in ["zec", "doge"]:
        try:
            # https://zcash.github.io/rpc/sendtoaddress.html
            # https://en.bitcoin.it/wiki/Original_Bitcoin_client/API_calls_list
            result = wallet.sendtoaddress(address, str(round(amount, 8)), "", "", True)
            return result            
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin in ["xmr", "wow"]:
        try:
            if coin == "xmr":
                atomic_units = Decimal("1e12")
            elif coin == "wow":
                atomic_units = Decimal("1e11")
            # https://monero-python.readthedocs.io/en/latest/transactions.html#sending-payments-1
            args = {
                "destinations": [{"address": address, "amount": int(amount*atomic_units)}],
                "mixin": 16
            }
            tx = wallet.transfer(args)
            return str(tx["tx_hash"])
        except XmrJSONRPCException as e:
            raise WalletEx(e)
    else:
        raise WalletEx("Unsupported coin: {} in lib.wallets.send()".format(coin))

# Estimate TX fee
def estimate_tx_fee(coin):
    if coin in ["btc", "ltc", "dash"]:
        wallet = get_wallet(coin)
        try:
            # https://getblock.io/docs/available-nodes-methods/BTC/JSON-RPC/estimatesmartfee/
            result = wallet.estimatesmartfee(2)
            if "errors" in result and len(result["errors"]) > 0:
                raise WalletEx(result["errors"])
            return Decimal(result["feerate"]/Decimal(2.0))  # Avg tx is about half a kb
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin == "bch":
        wallet = get_wallet(coin)
        try:
            # https://docs.bitcoincashnode.org/doc/json-rpc/estimatefee/
            result = wallet.estimatefee()
            return Decimal(result/Decimal(2.0))  # Avg tx is about half a kb
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin == "doge":
        wallet = get_wallet(coin)
        try:
            # https://en.bitcoin.it/wiki/Original_Bitcoin_client/API_calls_list
            result = wallet.estimatefee(2)
            if result < 0:
                result = Decimal(0.01)
            return Decimal(result/Decimal(2.0))  # Avg tx is about half a kb
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin == "zec":
        wallet = get_wallet(coin)
        try:
            # https://zcash.github.io/rpc/estimatefee.html
            result = wallet.estimatefee(2)
            if result == -1:
                result = Decimal(0.00015)
            return Decimal(result*Decimal(5))  # Avg tx is about 5 kb
        except BtcJSONRPCException as e:
            raise WalletEx(e)
    elif coin in ["xmr", "wow"]:
        daemon = get_daemon(coin)
        try:
            if coin == "xmr":
                atomic_units = Decimal("1e12")
            elif coin == "wow":
                atomic_units = Decimal("1e11")
            # https://www.getmonero.org/resources/developer-guides/daemon-rpc.html#get_fee_estimate
            result = daemon.get_fee_estimate()
            # Estimated fee per byte in atomic units
            fee = Decimal(result["fee"]) / atomic_units * Decimal(2.5 * 1024) # Avg tx is about 2.5 kB
            return fee
        except XmrJSONRPCException as e:
            raise WalletEx(e)
    else:
        raise WalletEx("Unsupported coin: {} in lib.wallets.estimate_tx_fee()".format(coin))



if __name__ == "__main__":
    balance = wallet_balance("wow")
    print(f"wow wallet balance: {balance}")


    txid = send('zec', Decimal(0.001), "tmCnc6GeXerCxdVhZkj6nUYiNUoascDVhTX")

    rtxs = get_recv_tx_list('zec', 'utest1kqme0x9700vq47zwg07h3zmeh3fgegcxykvvjp7ckq7xazmjyceppv03h22qwvtm3vxlsddpmj7ut66j9ytkhqd2309dchghen3etpvuusfepetuszn9s5cghmcrrlx2yavl2hxqtvq')
    for rtx in rtxs:
        print(get_recv_tx('zec', rtx))

    balance = wallet_balance("zec")

    balance = wallet_balance("btc")
    print(f"btc wallet balance: {balance}")
    balance = wallet_balance("xmr")
    print(f"xmr wallet balance: {balance}")
    balance = wallet_balance("ltc")
    print(f"ltc wallet balance: {balance}")
    balance = wallet_balance("bch")
    print(f"bch wallet balance: {balance}")
    balance = wallet_balance("zec")
    print(f"zec wallet balance: {balance}")

    print(estimate_tx_fee("btc"))
    print(estimate_tx_fee("xmr"))
    print(estimate_tx_fee("ltc"))
    print(estimate_tx_fee("bch"))
    print(estimate_tx_fee("zec"))
    
    tx_data = get_recv_tx("xmr", "0dfe03db1996c77bb9a9eb959c24af8b1b54e3585b178e38ce399a851c076d64")
    print("in: ",tx_data)
    tx_data = get_send_tx("xmr", "48d82cff182545b7faf801a610eceffc3001d601a61dbf092a57a02f6ed71c98")
    print("out: ",tx_data)

    tx_data = get_recv_tx("btc", "e39697615e994c2668e55d43b65daaf5ef8934c00cdc28fd691b9e58e11ce495") # in
    print("in: ",tx_data)
    tx_data = get_send_tx("btc", "db3d55051b6832f4532e324eec0b528ae07cd9c69eadf3ae1c49f90d5bb43373") # out
    print("out: ", tx_data)
    
    tx_data = get_recv_tx("ltc", "e2ceff8ef62006c16bf62f64eb8257485b0dd90e9c7d7e819ec4a722f4e1ecae") # in
    print("in: ",tx_data)
#    tx_data = get_send_tx("ltc", "xxx") # out
#    print("out: ", tx_data)

    tx_data = get_recv_tx("bch", "fd5112ff48099d6a0e06700cff75fbc33a74b977a1d99f4d91fee831869b4368") # in
    print("in: ",tx_data)
#    tx_data = get_send_tx("bch", "xxx") # out
#    print("out: ", tx_data)

    tx_data = get_recv_tx("zec", "c1f4febf84735fdf3d225d47f57f5b6350afc5dc35c263e4414810b42c4aece1") # in
    print("in: ",tx_data)
    tx_data = get_send_tx("zec", "31e70228e20b9cbb30a5552074aafd951b04afcd085d8ecdac07cbcf2f31e4b2") # out
    print("out: ", tx_data)

    print(send_tx_confirmed("xmr", "48d82cff182545b7faf801a610eceffc3001d601a61dbf092a57a02f6ed71c98"))
    print(send_tx_confirmed("btc", "dc01f872569604d9533e36a7da614a6d4f09abb0eb1cff546f3037ad88adeea5"))
#    print(send_tx_confirmed("ltc", "xxx"))
#    print(send_tx_confirmed("bch", "xxx"))
    print(send_tx_confirmed("zec", "xxx"))


    print(get_recv_tx_list("btc", "tb1qw9p3tfklrpxqcd4uava6yaakflvwgccaxlcuel"))
    print(get_recv_tx_list("btc", "tb1qh73vk0se7ssu32fjg7q85k43sz9wx24crp339j"))
    print(get_recv_tx_list("xmr", "73Wmgru9eGLMDCwQ8GPEbJRxV9akc5eQiQtccfS67YMBekiicRLjWAWWtYLUcs2sy5Sx9N9CXwjRC7tTHttkcEnF9tw8MpB"))
    print(get_recv_tx_list("ltc", "tltc1q54h36eykleulhfxr3paq9k80fkys77k9z5gdk0"))
#    print(get_recv_tx_list("bch", "xxx"))
    print(get_recv_tx_list("zec", "xxx"))

    ltc_tx = send("ltc", Decimal(0.0000154), "QYxQ2VLZo7HaHNqtL8hg1HokjQoeDyWULz")
    print(ltc_tx)
    bch_tx = send("bch", Decimal(0.0000154), "xxx")
    print(bch_tx)
    zec_tx = send("zec", Decimal(0.0000154), "xxx")
    print(zec_tx)    
    while True:
        tx_data = get_send_tx("ltc", ltc_tx)
        print("ltc sent: ",tx_data)
        tx_data = get_send_tx("bch", bch_tx)
        print("bch sent: ",tx_data)
        tx_data = get_send_tx("zec", bch_tx)
        print("zec sent: ",tx_data)

#    btc_tx = send("btc", Decimal(0.0000123), "tb1qjv3023canpmnn89mflfwq9ywzyyd3z3ws6aye0")
#    xmr_tx = send("xmr", Decimal(1.23), "7AKNreg2nUPW3Vx3DGJVkTDqCDZnWA9fTYMVhUpgBCjLBq5TC8Qc5sF2x9ysHetivvNJxq7YpMdaySNBS3nzqB7QSTSqMHE")
#    print(xmr_tx)
#    import time
#    while True:
#        tx_data = get_send_tx("xmr", xmr_tx)
#        print("sent: ",tx_data)
#        tx_data = get_send_tx("btc", btc_tx) # out
#        print("sent: ", tx_data)
#        time.sleep(1)
