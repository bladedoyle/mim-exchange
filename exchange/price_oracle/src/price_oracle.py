#!/usr/bin/env python3

from decimal import Decimal
from datetime import timedelta
from lib.timestamp import epoch_now
import time
import sys
import traceback

from lib.tradeogre import TradeOgre
from lib.coingecko import CoinGeckoAPI
from lib.kucoin import MarketData
from lib.kraken import KrakenApi
from lib.okx import OkxApi

# Logging
from lib.logger import Logger

import redis
import json

REFRESH_SECONDS = 500

ALTS = [
    "xmr",
    "zec",
    "ltc",
    "bch",
    "dash",
    "doge",
    "wow",
    "usd",
]

class PriceOracle():
    def __init__(self):
        self.logger = Logger(log_level="INFO")
        self.tradeogre = TradeOgre()
        self.coingecko = CoinGeckoAPI()
        self.kucoin = MarketData()
        self.kraken = KrakenApi()
        self.okx =  OkxApi()
        self.redis = redis.Redis(host='redis', port=6379, db=0)
        self.redis.ping()

    def dumps(self, data):
        d = {}
        for k, v in data.items():
            if type(v) == Decimal:
                d[k] = str(round(v, 12))
            else:
                d[k] = v
        j = json.dumps(d)
        return j

    def save(self, market):
        name = "prices"
        for pair, prices in market.items():
            value = self.dumps(prices)
            self.redis.hset(name, pair, value)

    def run(self):
        while True:
            self.logger.info("Begin Price Check...")
            try:
                config = json.loads(self.redis.get("config").decode())
                if config is None:
                    self.logger.error("Config not found in database, please create it")
                    sys.exit(1)
                expire_seconds = int(timedelta(minutes=int(config["price_data_expire"])).total_seconds())
                market = {}
                ##
                # Get base pairs:  
                #   from_coin -> BTC
                for coin in ALTS:
                    method = f"{coin}_btc"
                    m = globals()['PriceOracle']()
                    func = getattr(m, method)
                    prices = func()
                    pair = f"{coin}-btc"
                    if len(prices) < 1:
                        raise Exception(f"Error checking {pair}: Not enough data available: {len(prices)}")
                    else:
                        self.logger.info(f"Calculating {pair} with {len(prices)} values")
                        market[pair] = {
                            "price": sum(prices)/len(prices),
                            "expire": epoch_now() + expire_seconds,
                        }

                ##
                # Calculate inverted base pairs
                #   BTC -> from_coin
                for coin in ALTS:
                    pair = f"btc-{coin}"
                    basepair = f"{coin}-btc"
                    self.logger.info(f"Calculating {pair}")
                    market[pair] = {
                        "price": Decimal(1)/market[basepair]["price"],
                        "expire": market[basepair]["expire"],
                    }
                
                ##
                # Calculate alt pairs
                for from_coin in ALTS:
                    for to_coin in ALTS:
                        pair = f"{from_coin}-{to_coin}"
                        from_coin_btc = market[f"{from_coin}-btc"]["price"]
                        to_coin_btc = market[f"{to_coin}-btc"]["price"]
                        self.logger.info(f"Calculating {pair}")
                        market[pair] = {
                            "price": from_coin_btc/to_coin_btc,
                            "expire": min(market[f"{from_coin}-btc"]["expire"], market[f"{to_coin}-btc"]["expire"]),
                        }

                
                ##
                # Sanity check by getting USD prices from exchanges
                prices = self.xmr_usd()
                xmr_usd = sum(prices)/len(prices)
                if abs(xmr_usd/market["xmr-usd"]["price"]) < 0.01:
                     self.logger.warning("Calcualte XMR-USD has high spread: {} vs {}")
                # XXX TODO - the others

                # Save to redis
                self.save(market)

            except Exception as e:
                tb = traceback.format_exc()
                self.logger.error("ERROR: {} - {}".format(str(e), tb))
                time.sleep(60) 

            self.logger.info(market)
            self.logger.info("Done")
            time.sleep(REFRESH_SECONDS)



    def xmr_btc(self):
        prices = []
        try:
            # Get TradeOgre Price
            data = self.tradeogre.ticker("BTC-XMR")
            if data["success"] == True:
                prices.append(Decimal(data["price"]))
        except Exception as e:
            self.logger.warning(f"geting Trade Ogre market xmr_btc: {str(e)}")
        try:
            # Get kucoin price
            price = self.kucoin.get_ticker('XMR-BTC')
            if "price" in price:
                prices.append(Decimal(price["price"]))
        except Exception as e:
            self.logger.warning(f"geting Kucoin market xmr_btc: {str(e)}")
        try:
            # Get Kraken price
            price = self.kraken.get_ticker("XXMRXXBT")["XXMRXXBT"]["a"][0]
            prices.append(Decimal(price))
        except Exception as e:
            self.logger.warning(f"geting Kraken market xmr_btc: {str(e)}")
        try:
            # Get OKX price
            price = self.okx.get_ticker('XMR-BTC')[0]["last"]
            prices.append(Decimal(price))
        except Exception as e:
            self.logger.warning(f"geting OKX market xmr_btc: {str(e)}")
        try:
            # Get CoinGecko Price
            data = self.coingecko.get_coin_by_id("monero")
            prices.append(Decimal(data["market_data"]["current_price"]["btc"]))
        except Exception as e:
            self.logger.warning(f"geting CoinGecko market xmr-btc: {str(e)}")
        return prices


    def wow_btc(self):
        prices = []
        try:
            # Get CoinGecko Price
            data = self.coingecko.get_coin_by_id("wownero")
            prices.append(Decimal(data["market_data"]["current_price"]["btc"]))
        except Exception as e:
            self.logger.warning(f"geting CoinGecko market wow_btc: {str(e)}")
        try:
            # Get TradeOgre Price
            data = self.tradeogre.ticker("BTC-WOW")
            if data["success"] == True:
                prices.append(Decimal(data["price"]))
        except Exception as e:
            self.logger.warning(f"geting Trade Ogre market wow_btc: {str(e)}")
        return prices


    def usd_btc(self):
        prices = []
        try:
            # Get CoinGecko Price
            bitcoin = self.coingecko.get_coin_by_id("bitcoin")
            prices.append(Decimal(1.0)/Decimal(bitcoin["market_data"]["current_price"]["usd"]))
        except Exception as e:
            self.logger.warning(f"geting CoinGecko market usd_btc: {str(e)}")
        try:
            # Get kucoin price
            price = self.kucoin.get_ticker('BTC-USDT')
            if "price" in price:
                prices.append(Decimal(1.0)/Decimal(price["price"]))
        except Exception as e:
            self.logger.warning(f"geting Kucoin market usd_btc: {str(e)}")
        try:
            # Get Kraken price
            price = self.kraken.get_ticker("XXBTZUSD")["XXBTZUSD"]["a"][0]
            prices.append(Decimal(1.0)/Decimal(price))
        except Exception as e:
            self.logger.warning(f"geting Kraken market use_btc: {str(e)}")
        try:
            # Get OKX price
            price = self.okx.get_ticker('BTC-USDT')[0]["last"]
            prices.append(Decimal(1.0)/Decimal(price))
            price = self.okx.get_ticker('BTC-USDC')[0]["last"]
            prices.append(Decimal(1.0)/Decimal(price))
        except Exception as e:
            self.logger.warning(f"geting OKX market usd_btc: {str(e)}")
        return prices


    def ltc_btc(self):
        prices = []
        try:
            # Get TradeOgre Price
            data = self.tradeogre.ticker("LTC-BTC")
            if data["success"] == True:
                prices.append(Decimal(data["price"]))
        except Exception as e:
            self.logger.warning(f"geting Trade Ogre market ltc_btc: {str(e)}")
        try:
            # Get kucoin price
            price = self.kucoin.get_ticker('LTC-BTC')
            if "price" in price:
                prices.append(Decimal(price["price"]))
        except Exception as e:
            self.logger.warning(f"geting Kucoin market ltc_btc: {str(e)}")
        try:
            # Get Kraken price
            price = self.kraken.get_ticker("XLTCXXBT")["XLTCXXBT"]["a"][0]
            prices.append(Decimal(price))
        except Exception as e:
            self.logger.warning(f"geting Kraken market ltc_btc: {str(e)}")
        try:
            # Get OKX price
            price = self.okx.get_ticker('LTC-BTC')[0]["last"]
            prices.append(Decimal(price))
        except Exception as e:
            self.logger.warning(f"geting OKX market ltc_btc: {str(e)}")
        try:
            # Get CoinGecko Price
            data = self.coingecko.get_coin_by_id("litecoin")
            prices.append(Decimal(data["market_data"]["current_price"]["btc"]))
        except Exception as e:
            self.logger.warning(f"geting CoinGecko market ltc_btc: {str(e)}")
        return prices


    def dash_btc(self):
        prices = []
        try:
            # Get TradeOgre Price
            data = self.tradeogre.ticker("DASH-BTC")
            if data["success"] == True:
                prices.append(Decimal(data["price"]))
        except Exception as e:
            self.logger.warning(f"geting Trade Ogre market dash_btc: {str(e)}")
        try:
            # Get kucoin price
            price = self.kucoin.get_ticker('DASH-BTC')
            if "price" in price:
                prices.append(Decimal(price["price"]))
        except Exception as e:
            self.logger.warning(f"geting Kucoin market dash_btc: {str(e)}")
        try:
            # Get Kraken price
            price = self.kraken.get_ticker("DASHXBT")["DASHXBT"]["a"][0]
            prices.append(Decimal(price))
        except Exception as e:
            self.logger.warning(f"geting Kraken market dash_btc: {str(e)}")
        try:
            # Get OKX price
            price = self.okx.get_ticker('DASH-BTC')[0]["last"]
            prices.append(Decimal(price))
        except Exception as e:
            self.logger.warning(f"geting OKX market dash_btc: {str(e)}")
        try:
            # Get CoinGecko Price
            data = self.coingecko.get_coin_by_id("dash")
            prices.append(Decimal(data["market_data"]["current_price"]["btc"]))
        except Exception as e:
            self.logger.warning(f"geting CoinGecko market dash_btc: {str(e)}")
        return prices


    def doge_btc(self):
        prices = []
        try:
            # Get TradeOgre Price
            data = self.tradeogre.ticker("DOGE-BTC")
            if data["success"] == True:
                prices.append(Decimal(data["price"]))
        except Exception as e:
            self.logger.warning(f"geting Trade Ogre market doge_btc: {str(e)}")
        try:
            # Get kucoin price
            price = self.kucoin.get_ticker('DOGE-BTC')
            if "price" in price:
                prices.append(Decimal(price["price"]))
        except Exception as e:
            self.logger.warning(f"geting Kucoin market doge_btc: {str(e)}")
        try:
            # Get Kraken price
            price = self.kraken.get_ticker("DOGEXBT")["XXDGXXBT"]["a"][0]
            prices.append(Decimal(price))
        except Exception as e:
            self.logger.warning(f"geting Kraken market doge_btc: {str(e)}")
        try:
            # Get OKX price
            price = self.okx.get_ticker('DOGE-BTC')[0]["last"]
            prices.append(Decimal(price))
        except Exception as e:
            self.logger.warning(f"geting OKX market doge_btc: {str(e)}")
        try:
            # Get CoinGecko Price
            data = self.coingecko.get_coin_by_id("dogecoin")
            prices.append(Decimal(data["market_data"]["current_price"]["btc"]))
        except Exception as e:
            self.logger.warning(f"geting CoinGecko market doge_btc: {str(e)}")
        return prices
    

    def bch_btc(self):
        prices = []
        try:
            # Get kucoin price
            price = self.kucoin.get_ticker('BCH-BTC')
            if "price" in price:
                prices.append(Decimal(price["price"]))
        except Exception as e:
            self.logger.warning(f"geting Kucoin market bch_btc: {str(e)}")
        try:
            # Get Kraken price
            price = self.kraken.get_ticker("BCHXBT")["BCHXBT"]["a"][0]
            prices.append(Decimal(price))
        except Exception as e:
            self.logger.warning(f"geting Kraken market bch_btc: {str(e)}")
        try:
            # Get OKX price
            price = self.okx.get_ticker('BCH-BTC')[0]["last"]
            prices.append(Decimal(price))
        except Exception as e:
            self.logger.warning(f"geting OKX market bch_btc: {str(e)}")
        try:
            # Get CoinGecko Price
            data = self.coingecko.get_coin_by_id("bitcoin-cash")
            prices.append(Decimal(data["market_data"]["current_price"]["btc"]))
        except Exception as e:
            self.logger.warning(f"geting CoinGecko market bch_btc: {str(e)}")
        return prices

    def zec_btc(self):
        prices = []
        try:
            # Get kucoin price
            price = self.kucoin.get_ticker('ZEC-BTC')
            if "price" in price:
                prices.append(Decimal(price["price"]))
        except Exception as e:
            self.logger.warning(f"geting Kucoin market zec_btc: {str(e)}")
        try:
            # Get Kraken price
            price = self.kraken.get_ticker("XZECXXBT")["XZECXXBT"]["a"][0]
            prices.append(Decimal(price))
        except Exception as e:
            self.logger.warning(f"geting Kraken market zec_btc: {str(e)}")
        try:
            # Get OKX price
            price = self.okx.get_ticker('ZEC-BTC')[0]["last"]
            prices.append(Decimal(price))
        except Exception as e:
            self.logger.warning(f"geting OKX market zec_btc: {str(e)}")
        try:
            # Get CoinGecko Price
            data = self.coingecko.get_coin_by_id("zcash")
            prices.append(Decimal(data["market_data"]["current_price"]["btc"]))
        except Exception as e:
            self.logger.warning(f"geting CoinGecko market zec_btc: {str(e)}")
        return prices


    ##
    # Also get each coins USD value as a double check
    def xmr_usd(self):
        prices = []
        try:
            # Get CoinGecko Price
            data = self.coingecko.get_coin_by_id("monero")
            prices.append(Decimal(data["market_data"]["current_price"]["usd"]))
        except Exception as e:
            self.logger.warning(f"geting CoinGecko market xmr-usd: {str(e)}")
        try:
            # Get kucoin price
            price = self.kucoin.get_ticker('XMR-USDT')
            if "price" in price:
                prices.append(Decimal(price["price"]))
        except Exception as e:
            self.logger.warning(f"geting Kucoin market xmr-usd: {str(e)}")
        # Get Kraken price
        try:
            price = self.kraken.get_ticker("XXMRZUSD")["XXMRZUSD"]["a"][0]
            prices.append(Decimal(price))
        except Exception as e:
            self.logger.warning(f"geting Kraken market xmr-usd: {str(e)}")
        # Get OKX price
        try:
            price = self.okx.get_ticker('XMR-USDT')[0]["last"]
            prices.append(Decimal(price))
            price = self.okx.get_ticker('XMR-USDC')[0]["last"]
            prices.append(Decimal(price))
        except Exception as e:
            self.logger.warning(f"geting OKX market xmr-usd: {str(e)}")
        return prices


if __name__ == "__main__":
    price_oracle = PriceOracle()
    price_oracle.run()