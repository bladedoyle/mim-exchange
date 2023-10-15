import os
from lib.wallets import get_wallet
# qrcode
import qrcode
import base64
import io


def is_valid(coin, address):
    wallet = get_wallet(coin)
    if coin in ["btc", "ltc", "bch", "zec", "dash", 'doge']:
        result = wallet.validateaddress(address)
        return result["isvalid"]
    elif coin in ["xmr", "wow"]:
        result = wallet.validate_address({"address": address})
        return result["valid"]
    else:
        return False

def get_new(coin):
    wallet = get_wallet(coin)
    if coin in ["btc", "ltc", "bch", "dash", 'doge']:
        address = wallet.getnewaddress()
        return (address, address,)
    elif coin == "zec":
        # https://zcash.github.io/rpc/z_getaddressforaccount.html
        unified_address = wallet.z_getaddressforaccount(0, ["p2pkh",'sapling'])["address"]
        # https://zcash.github.io/rpc/z_listunifiedreceivers.html
        unified_receivers = wallet.z_listunifiedreceivers(unified_address)
        return (unified_receivers["p2pkh"], unified_address,)
    elif coin in ["xmr", "wow"]:
        address = wallet.create_address({"account_index": 0})
        return (address["address"], address["address"],)
    else:
        return None

def get_qrcode(coin, address):
    qr = qrcode.QRCode(
        # integer from 1 to 40 that controls the size of the QR Code
        version=1,
        # error_correction parameter controls the error correction used for the QR Code
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        # box_size parameter controls how many pixels each “box” of the QR code is.
        box_size=8,
        # border parameter controls how many boxes thick the border should be.
        # the default is 4, which is the minimum
        border=4,
    )
    # add your text here
    qr.add_data(address)
    qr.make(fit=True)

    # change the colors of the QR code
    img = qr.make_image(back_color="#F8F8F8", fill_color="#181818")
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG', quality=90)
    img_io.seek(0)
    return base64.b64encode(img_io.getvalue()).decode()

def shorten(address, length):
    if len(address) > length:
        half = int(length/2) - 3
        return address[:half] + "......" + address[-half:]
    else:
        return address


if __name__ == "__main__":
    address = get_new("doge")
    print(address)
    print(is_valid('doge', address[0]))
    print(is_valid('doge', "tb1q7hp978d6txqcuqpgmuaym4zyxdkuq4s4nhgd29"))

    address = get_new("dash")
    print(address)
    print(is_valid('dash', address[0]))
    print(is_valid('dash', "tb1q7hp978d6txqcuqpgmuaym4zyxdkuq4s4nhgd29"))
    print(get_new("zec"))
    print(is_valid("xmr", "73Wmgru9eGLMDCwQ8GPEbJRxV9akc5eQiQtccfS67YMBekiicRLjWAWWtYLUcs2sy5Sx9N9CXwjRC7tTHttkcEnF9tw8MpB"))
    print(is_valid("xmr", "7AWqKqtvSb7Ubv87is17qnMGaWLsGsJy1UL4WYLU13noUPi4QoYN54HSYFKwdzV9P8e8eLvsPmTNqbaWnsFS45m8UCowWLb"))
    print(is_valid("btc", "tb1q7hp978d6txqcuqpgmuaym4zyxdkuq4s4nhgd29"))
    print(is_valid("btc", "tb1q7hp978d6txqcuqpgmuaym4zyxdkuq4s4nhgd20"))
    print(is_valid("bch", "bchtest:qpmxeatf3dfuypj6g3ll6g7f9szyjfmwdq0ajfjcy4"))
    print(is_valid("zec", "utest18lav0f86l4chms4tjel06x6kshg7qea7keeu0luxyyjrf5q988hzgyx0h43v3gn0k6w009mknkfwd9vaqr4l08ykhtdsqe6fau2freq90ude5gmssjw6aaqmu9m6rmvfvgwqhw46dn72mzjd9h25d57c62fj0htk8y0arm3dgmhfd4lgffkz7d56cvd06hknyfjsl4epheyr56k5ry7"))
    print(is_valid("zec", "utest.x46jp2ekppky48w3smju5jclwcw8wwe979s27ggq4gavy7asmw0h5gzlq3ewtnv9xfntv8kee73v7hhfzltkauxslrv444cajwu5qp5q05sgc2s2zyfdc3lwwcf2kmytzkxm89gty8galg5heg70l00c69sklnnvg0nzlj99nqzkz6sjuq74p6gver3n089pp6fjxfj0skw9lgql9"))
    print(get_new("xmr"))
    print(get_new("btc"))
    print(get_new("bch"))
    print(get_new("zec"))