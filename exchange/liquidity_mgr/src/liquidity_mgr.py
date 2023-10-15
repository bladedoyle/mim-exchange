#!/usr/bin/env python3

from decimal import Decimal
import time
import traceback

from lib import wallets
from lib.logger import Logger

import redis
import json


class LiquidityMgr():
    def __init__(self):
        self.logger = Logger(log_level="INFO")
        self.redis = redis.Redis(host='redis', port=6379, db=0)
        self.redis.ping()
        self.logger.warning("Liquidity Manager Started")

    def update_tx_fees(self):
        self.logger.info("Tx Fees check...")
        try:
            # Get fees
            # XMR
            try:
                xmr_fee = wallets.estimate_tx_fee("xmr")
            except Exception as e:
                self.logger.error(f"Failed to get tx fee for xmr: {str(e)}")
                xmr_fee = Decimal(0.0003)
            # WOW
            try:
                wow_fee = wallets.estimate_tx_fee("wow")
            except Exception as e:
                self.logger.error(f"Failed to get tx fee for wow: {str(e)}")
                wow_fee = Decimal(0.0003)
            # BTC
            try:
                btc_fee = wallets.estimate_tx_fee("btc")
            except Exception as e:
                self.logger.error(f"Failed to get tx fee for btc: {str(e)}")
                btc_fee = Decimal(0.00002)
            # LTC
            try:
                ltc_fee = wallets.estimate_tx_fee("ltc")
            except Exception as e:
                self.logger.error(f"Failed to get tx fee for ltc: {str(e)}")
                ltc_fee = Decimal(0.0001)
            # BCH
            try:
                bch_fee = wallets.estimate_tx_fee("bch")
            except Exception as e:
                self.logger.error(f"Failed to get tx fee for bch: {str(e)}")
                bch_fee = Decimal(0.0001)
            # ZEC
            try:
                zec_fee = wallets.estimate_tx_fee("zec")
            except Exception as e:
                self.logger.error(f"Failed to get tx fee for zec: {str(e)}")
                zec_fee = Decimal(0.0005)
            # DASH
            try:
                dash_fee = wallets.estimate_tx_fee("dash")
            except Exception as e:
                self.logger.error(f"Failed to get tx fee for dash: {str(e)}")
                dash_fee = Decimal(0.00006)
            # DOGE
            try:
                doge_fee = wallets.estimate_tx_fee("doge")
            except Exception as e:
                self.logger.error(f"Failed to get tx fee for doge: {str(e)}")
                doge_fee = Decimal(0.005)                            
            fees = {
                "xmr": str(round(Decimal(xmr_fee), 12)),
                "btc": str(round(Decimal(btc_fee), 12)),
                "ltc": str(round(Decimal(ltc_fee), 12)),
                "bch": str(round(Decimal(bch_fee), 12)),
                "zec": str(round(Decimal(zec_fee), 12)),
                "dash": str(round(Decimal(dash_fee), 12)),
                "doge": str(round(Decimal(doge_fee), 12)),
                "wow": str(round(Decimal(wow_fee), 12)),
            }
            # Update tx_fees in db
            self.logger.info(fees)

            # Save to redis
            key = "tx_fees"
            value = json.dumps(fees)
            self.redis.set(key, value, ex=3600)
            self.logger.info("Completed tx fee check")
            
        except Exception as e:
            tb = traceback.format_exc()
            self.logger.error("ERROR: {} - {}".format(str(e), tb))


    def update_balances(self):
        self.logger.info("Wallet Balance Check...")
        try:
            # Get current balances
            try:
                xmr_balance = wallets.wallet_balance("xmr")
            except Exception as e:
                self.logger.error(f"Failed to get balance for xmr: {str(e)}")
                xmr_balance = str(Decimal(0.0))
            try:
                btc_balance = wallets.wallet_balance("btc")
            except Exception as e:
                self.logger.error(f"Failed to get balance for btc: {str(e)}")
                btc_balance = str(Decimal(0.0))
            try:
                ltc_balance = wallets.wallet_balance("ltc")
            except Exception as e:
                self.logger.error(f"Failed to get balance for ltc: {str(e)}")
                ltc_balance = str(Decimal(0.0))
            try:
                bch_balance = wallets.wallet_balance("bch")
            except Exception as e:
                self.logger.error(f"Failed to get balance for bch: {str(e)}")
                bch_balance = str(Decimal(0.0))
            try:
                zec_balance = wallets.wallet_balance("zec")
            except Exception as e:
                self.logger.error(f"Failed to get balance for zec: {str(e)}")
                zec_balance = str(Decimal(0.0))
            try:
                dash_balance = wallets.wallet_balance("dash")
            except Exception as e:
                self.logger.error(f"Failed to get balance for dash: {str(e)}")
                dash_balance = str(Decimal(0.0))
            try:
                doge_balance = wallets.wallet_balance("doge")
            except Exception as e:
                self.logger.error(f"Failed to get balance for doge: {str(e)}")
                doge_balance = str(Decimal(0.0))
            try:
                wow_balance = wallets.wallet_balance("wow")
            except Exception as e:
                self.logger.error(f"Failed to get balance for wow: {str(e)}")
                wow_balance = str(Decimal(0.0))
            balances = {
                "xmr": xmr_balance,
                "btc": btc_balance,
                "ltc": ltc_balance,
                "bch": bch_balance,
                "zec": zec_balance,
                "dash": dash_balance,
                "doge": doge_balance,
                "wow": wow_balance,
            }
            self.logger.info(balances)

            # Save to redis
            key = "wallet_balances"
            value = json.dumps(balances)
            self.redis.set(key, value, ex=600)
            self.logger.info("Completed wallet balance check")
            
        except Exception as e:
            tb = traceback.format_exc()
            self.logger.error("ERROR: {} - {}".format(str(e), tb))


    def run(self):
        try:
            while True:
                self.update_balances()
                self.update_tx_fees()
                time.sleep(60)
        except Exception as e:
            tb = traceback.format_exc()
            self.logger.error("ERROR: {} - {}".format(str(e), tb))
            time.sleep(60)    


if __name__ == "__main__":
    mgr = LiquidityMgr()
    mgr.run()
