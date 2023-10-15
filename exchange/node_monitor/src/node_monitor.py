#!/usr/bin/env python3

from decimal import Decimal
import time
import traceback

from lib import wallets
from lib.logger import Logger

import redis
import json


class NodeMonitor():
    def __init__(self):
        self.coin_list = ["btc", "xmr", "zec", "ltc", "bch", "dash", "doge", "wow"]
        self.logger = Logger(log_level="INFO")
        self.redis = redis.Redis(host='redis', port=6379, db=0)
        self.redis.ping()

        self.logger.warning(f"Node Monitor Started on coins: {self.coin_list}")

    def check(self):
        broken_wallets = []
        for coin in self.coin_list:
            try:
                wallets.health(coin)
            except Exception as e:
                self.logger.error(f"Wallet or Node Broken for {coin}: {str(e)}")
                broken_wallets.append(coin)
        return broken_wallets
    
    def save(self, broken_coins):
        # Save to redis
        key = "broken_coins"
        value = json.dumps(broken_coins)
        self.redis.set(key, value)

    def run(self):
        try:
            while True:
                self.logger.info(f"Node Monitor checking start")
                broken_coins = self.check()
                self.save(broken_coins)
                self.logger.info(f"Node Monitor checking end")
                time.sleep(60)
        except Exception as e:
            tb = traceback.format_exc()
            self.logger.error("ERROR: {} - {}".format(str(e), tb))
            time.sleep(60)    


if __name__ == "__main__":
    mgr = NodeMonitor()
    mgr.run()
