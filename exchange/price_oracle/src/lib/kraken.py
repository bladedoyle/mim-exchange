#!/usr/bin/env python3

import requests


class KrakenApiEx(Exception):
    pass

class KrakenApi(object):
    def __init__(self):
        self.api_domain = "https://api.kraken.com"
        self.api_path = "/0/public/"
        self.api_method = "Ticker"

    def get_ticker(self, pair=None):
        pair_data = ""
        if pair is not None:
            pair_data = f"pair={pair}"
        api_request = requests.get(
            url=self.api_domain + self.api_path + self.api_method + '?' + pair_data,
            headers={"User-Agent": "Kraken REST API"}
        )
        api_reply = api_request.json()
        if "error" in api_reply and len(api_reply["error"]) > 0:
            raise KrakenApiEx(str(api_reply["errors"]))
        return api_reply["result"]

if __name__ == "__main__":
    k = KrakenApi()
    print(k.get_ticker("XXMRXXBT"))  # XMR-BTC
    print(k.get_ticker("XXMRZUSD"))  # XMR-USD

    print(k.get_ticker("XXBTZUSD"))  # BTC-USD

    print(k.get_ticker("XLTCXXBT"))  # LTC-BTC
    print(k.get_ticker("XLTCZUSD"))  # LTC-USD

    print(k.get_ticker("BCHXBT"))  # BCH - BTC
    print(k.get_ticker("BCHUSD"))  # BCH - USD

    print(k.get_ticker("XZECXXBT"))  # ZEC - BTC
    print(k.get_ticker("XZECZUSD"))  # ZEC - USD

    print(k.get_ticker("DASHXBT"))  # DASH - BTC
    print(k.get_ticker("DASHUSD"))  # DASH - USD

    print(k.get_ticker("DOGEXBT"))  # DOGE - BTC
    print(k.get_ticker("DOGEUSD"))  # DOGE - USD