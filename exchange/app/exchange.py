from datetime import datetime, timedelta
from decimal import Decimal

from lib.logger import Logger
from db import SwapDB
from lib.timestamp import epoch_now, epoch_at


class SwapEx(Exception):
    pass

# Get market prices and swap fees data
def calculate_swap(swap):
    logger = Logger(log_level="INFO")
    db = SwapDB()
    pair = f"{swap.swap_from}-{swap.swap_to}"
    exchange_rate_expire = int(db.get_config()["exchange_rate_expire"])
    price = db.get_prices()[pair]
    if price is None:
        raise SwapEx(f"Failed to get price data for {pair}")
    tx_fees = db.get_tx_fees()
    if tx_fees is None:
        raise SwapEx("Failed to get transaction fee data")
    # Get Exchange fee
    exchange_fee_pct = Decimal(db.get_config()["exchange_fee"])
    # Get transaction fee
    tx_fee = tx_fees[swap.swap_to]

    if swap.recvd_from == False:
        # Quote
        if swap.quoted_swap_expire_ts < epoch_now():
            # Get new rate and quote
            swap.quoted_exchange_rate = Decimal(price)
            swap.quoted_swap_expire_ts = epoch_at(datetime.utcnow() + timedelta(minutes=exchange_rate_expire))
            swap_fee = Decimal(swap.quoted_swap_from_amount) * (exchange_fee_pct * Decimal(.01))
            swap.quoted_swap_to_amount = (Decimal(swap.quoted_swap_from_amount) - swap_fee) * swap.quoted_exchange_rate
    elif swap.sent_to_confirmed == False:
        # Exchange - If the quote is still valid and the recvd amount is same as quoted, use quoted rate, else use market rate
        if swap.quoted_swap_expire_ts > epoch_now() and swap.quoted_swap_from_amount == swap.swap_from_amount:
            swap.exchange_rate = swap.quoted_exchange_rate
        else:
             swap.exchange_rate = Decimal(price)
        swap_fee = Decimal(swap.swap_from_amount) * (exchange_fee_pct * Decimal(.01))
        swap.swap_to_amount = ((Decimal(swap.swap_from_amount) - swap_fee) * swap.exchange_rate) - Decimal(tx_fee)
        logger.info(f"quoted_swap_to_amount: {swap.quoted_swap_to_amount}")
    else:
        raise Exception("Swap completed, should not calculate now")