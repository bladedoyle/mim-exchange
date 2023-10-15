import uuid
import json
from decimal import Decimal
from lib.timestamp import epoch_now

# A swap
class Swap:
    def __init__(self, data=None):
        if data is None:
            self.id = str(uuid.uuid4())[-12:]               # Exchange ID
            self.ts = epoch_now()                           # Exchange Created timestamp
            self.swap_from = None                           # Coin to swap from
            self.swap_to = None                             # Coin to swap to
            self.swap_from_address = None                   # Address for the user to send to (zcash p2pkh address)
            self.send_from_address = None                   # Address for the user to senf to (zcash unified address)
            self.swap_to_address = None                     # Address for us to send to
            self.quoted_swap_from_amount = Decimal(0.0)     # Quoted amount to be swapped from
            self.quoted_swap_to_amount = Decimal(0.0)       # Quoted amount swapped to
            self.quoted_exchange_rate = Decimal(0.0)        # Quoted exchange rate
            self.quoted_swap_expire_ts = epoch_now()        # Quoted exchange expire time
            self.swap_from_amount = Decimal(0.0)            # Amount swapped from
            self.swap_to_amount = Decimal(0.0)              # Amount swapped to
            self.exchange_rate = Decimal(0.0)               # Exchange rate swap was executed at
            self.swap_executed_ts = None                    # Timestamp the swap was executed
            self.sent_to_txid = None                        # Transaction id of send - set if we sent the tx
            self.recvd_from = False                         # Have we received a confirmed tx from the user
            self.sent_to_confirmed = False                  # The sent tx has been confirmed
            self.send_failed = False                        # The send failed
            self.refund_address = None                      # Refund address for swap_from coin
            self.refund_txid = None                         # Transaction id of refund - set if we sent the refund tx
            self.refund_confirmed = False                   # The refund tx has been confirmed
            self.extra_recvs = False                        # The swap_to_address received extra recv transactions
            self.extra_recv_txs = []                        # List of amounts of extra recvd txs (ordered by recv tx time)
            self.extra_refund_txids = []                    # List of refund txids for extra recvd txs (ordered by recv tx time)
        else:
            self.loads(data)

    def dict(self):
        return {
            "id": self.id,
            "ts": self.ts,
            "swap_from": self.swap_from,
            "swap_to": self.swap_to,
            "swap_from_address": self.swap_from_address,
            "send_from_address": self.send_from_address,
            "swap_to_address": self.swap_to_address,
            "quoted_swap_from_amount": str(Decimal(self.quoted_swap_from_amount)),
            "quoted_swap_to_amount": str(Decimal(self.quoted_swap_to_amount)),
            "quoted_exchange_rate": str(Decimal(self.quoted_exchange_rate)),
            "quoted_swap_expire_ts": self.quoted_swap_expire_ts,
            "swap_from_amount": str(Decimal(self.swap_from_amount)),
            "swap_to_amount": str(Decimal(self.swap_to_amount)),
            "exchange_rate": str(Decimal(self.exchange_rate)),
            "swap_executed_ts": self.swap_executed_ts if self.swap_executed_ts else None,
            "sent_to_txid": self.sent_to_txid,
            "recvd_from": bool(self.recvd_from),
            "sent_to_confirmed": bool(self.sent_to_confirmed),
            "send_failed": bool(self.send_failed),
            "refund_address": self.refund_address if self.refund_address else None,
            "refund_txid": self.refund_txid,
            "refund_confirmed": self.refund_confirmed,
            "extra_recvs": bool(self.extra_recvs),
            "extra_recv_txs": self.extra_recv_txs,
            "extra_refund_txids": self.extra_refund_txids,
        }

    ##
    # dumps and loads to/from JSON so we can store in redis
    def dumps(self):
        return json.dumps(self.dict())
    
    def loads(self, swap_data):
        if type(swap_data) == dict:
            s = swap_data
        else:
            s = json.loads(swap_data)
        self.id = s["id"]
        self.ts = s["ts"]
        self.swap_from = s["swap_from"]
        self.swap_to = s["swap_to"]
        self.swap_from_address = s["swap_from_address"]
        self.send_from_address = s["send_from_address"]
        self.swap_to_address = s["swap_to_address"]
        self.quoted_swap_from_amount = Decimal(s["quoted_swap_from_amount"])
        self.quoted_swap_to_amount = Decimal(s["quoted_swap_to_amount"])
        self.quoted_exchange_rate = Decimal(s["quoted_exchange_rate"])
        self.quoted_swap_expire_ts = s["quoted_swap_expire_ts"]
        self.swap_from_amount = Decimal(s["swap_from_amount"])
        self.swap_to_amount = Decimal(s["swap_to_amount"])
        self.exchange_rate = Decimal(s["exchange_rate"])
        self.swap_executed_ts = s["swap_executed_ts"] if s["swap_executed_ts"] else None
        self.sent_to_txid = s["sent_to_txid"]
        self.recvd_from = bool(s["recvd_from"])
        self.sent_to_confirmed = bool(s["sent_to_confirmed"])
        self.send_failed = bool(s["send_failed"])
        self.refund_address = s["refund_address"]
        self.refund_txid = s["refund_txid"]
        self.refund_confirmed = s["refund_confirmed"]
        self.extra_recvs = bool(s["extra_recvs"])
        self.extra_recv_txs = s["extra_recv_txs"]
        self.extra_refund_txids = s["extra_refund_txids"]