#!/usr/bin/env python3

import requests

class OkxApiEx(Exception):
    pass

class OkxApi(object):
    def __init__(self):
        self.api_domain = "https://www.okx.com"
        self.api_path = "/api/v5/"
        self.api_method = "market/ticker"

    def get_ticker(self, pair):
        pair_data = f"instId={pair}"
        api_request = requests.get(
            url=self.api_domain + self.api_path + self.api_method + '?' + pair_data,
            headers={"User-Agent": "OKX REST API"}
        )
        api_reply = api_request.json()
        if "code" in api_reply and api_reply["code"] != "0":
            raise OkxApiEx(str(api_reply["msg"]))
        return api_reply["data"]

if __name__ == "__main__":
    ok = OkxApi()
    print(ok.get_ticker("XMR-BTC"))
    print(ok.get_ticker("XMR-USDT"))
    print(ok.get_ticker("XMR-USDC"))
    
    print(ok.get_ticker("BTC-USDT"))
    print(ok.get_ticker("BTC-USDC"))

    print(ok.get_ticker("LTC-BTC"))
    print(ok.get_ticker("LTC-USDT"))
    print(ok.get_ticker("LTC-USDC"))

    print(ok.get_ticker("BCH-BTC"))
    print(ok.get_ticker("BCH-USDT"))
    print(ok.get_ticker("BCH-USDC"))

    print(ok.get_ticker("ZEC-BTC"))
    print(ok.get_ticker("ZEC-USDT"))
    print(ok.get_ticker("ZEC-USDC"))

    print(ok.get_ticker("DASH-BTC"))
    print(ok.get_ticker("DASH-USDT"))
    print(ok.get_ticker("DASH-USDC"))

    print(ok.get_ticker("DOGE-BTC"))
    print(ok.get_ticker("DOGE-USDT"))
    print(ok.get_ticker("DOGE-USDC"))