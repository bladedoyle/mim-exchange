import redis
import json

from lib.swap import Swap
from lib.timestamp import epoch_now


class SwapDB:
    def __init__(self):
        self._r = redis.Redis(host='redis', port=6379, db=0)
        self._r.ping()

    def ping(self):
        reply = self._r.ping()
        assert reply == True, "Database Ping Failed"
        return True

    # Write one or more app configuration values 
    def set_config(self, config):
        key = "config"
        value = json.dumps(config)
        self._r.set(key, value)

    # Get app configuration
    def get_config(self):
        key = "config"
        value = self._r.get(key)
        if value is None:
            return None
        return json.loads(value.decode())

    # Create or Update swap data
    def set_swap(self, swap):
        name = "swaps"
        key = swap.id
        value = swap.dumps()
        self._r.hset(name, key, value)

    # Get swap
    def get_swap(self, id):
        # Try active swaps
        name = "swaps"
        value = self._r.hget(name, id)
        if value is None:
            # Try completed swaps
            name = "completed_swaps"
            value = self._r.hget(name, id)
        if value is None:
            # Try Archived swaps
            name = "archived_swaps"
            value = self._r.hget(name, id)
        if value is None:
            return None
        swap = Swap(value.decode())
        return swap

    # Move a swap to completed
    def complete_swap(self, id):
        value = self._r.hget("swaps", id)
        if value is not None:
            swap = json.loads(value.decode())
            key = swap["id"]
            self._r.hset("completed_swaps", key, value)
            self._r.hdel("swaps", id)

    # Create or Update completed swap data
    def set_completed_swap(self, swap):
        name = "completed_swaps"
        key = swap.id
        value = swap.dumps()
        self._r.hset(name, key, value)

    # Move a swap to archived
    def archive_swap(self, id):
        value = self._r.hget("completed_swaps", id)
        if value is not None:
            swap = json.loads(value.decode())
            key = swap["id"]
            self._r.hset("archived_swaps", key, value)
            self._r.hdel("completed_swaps", id)

    # Delete a swap
    def del_swap(self, id):
        name = "swaps"
        self._r.hdel(name, id)
        name = "completed_swaps"
        self._r.hdel(name, id)
        name = "archived_swaps"
        self._r.hdel(name, id)

    # Get all active swaps
    def get_active_swaps(self):
        name = "swaps"
        values = self._r.hgetall(name)
        return {k.decode(): Swap(v.decode()) for k, v in values.items()}

    # Get all completed swaps
    def get_completed_swaps(self):
        name = "completed_swaps"
        values = self._r.hgetall(name)
        return {k.decode(): Swap(v.decode()) for k, v in values.items()}

    # Get all archived swaps
    def get_archived_swaps(self):
        name = "archived_swaps"
        values = self._r.hgetall(name)
        return {k.decode(): Swap(v.decode()) for k, v in values.items()}

    # Get price data
    def get_prices(self):
        name = "prices"
        values = self._r.hgetall(name)
        market = {}
        for k, v in values.items():
            pair = k.decode()
            value = json.loads(v.decode())
            price = None
            if value["expire"] >= epoch_now():
                price = value["price"]
            market[pair] = price
        return market

    # Get TX fees data
    def get_tx_fees(self):
        key = "tx_fees"
        value = self._r.get(key)
        if value is None:
            return None
        return json.loads(value.decode())

    # Get wallet balance data
    def get_balances(self):
        key = "wallet_balances"
        value = self._r.get(key)
        if value is None:
            return None
        return json.loads(value.decode())

    # Get broken coin list
    def get_broken(self):
        key = "broken_coins"
        value = self._r.get(key)
        if value is None:
            return None
        return json.loads(value.decode())

    # Set exchange heartbeat ts
    def set_exchange_heartbeat(self, value):
        key = "exchange_heartbeat_ts"
        self._r.set(key, value)

    # Get exchange heartbeat timestamp (as a string)
    def get_exchange_heartbeat(self):
        key = "exchange_heartbeat_ts"
        value = float(self._r.get(key).decode())
        return value

    # send lock
    def get_send_lock(self):
        key = "send_lock"
        value = self._r.get(key)
        if value == None:
            return None
        lock = value.decode()
        return lock

    def set_send_lock(self, id):
        key = "send_lock"
        value = json.dumps(id)
        self._r.set(key, value)

    def unset_send_lock(self):
        key = "send_lock"
        self._r.delete(key)


    # ---
    # DBA / debugging methods
    
    def del_all_completed(self):
        name = "completed_swaps"
        values = self._r.hgetall(name)
        for k,v in values.items():
            self._r.hdel(name, k)

    def dump_all(self):
        keys = self._r.keys('*')
        for key in keys:
            type = self._r.type(key)
            if type == b"string":
                val = self._r.get(key)
                print(f"Type: string:\n{key} {val}\n\n")
            if type == b"hash":
                vals = self._r.hgetall(key)
                print(f"Type hash:\n{key} {vals}\n\n")
            if type == b"zset":
                vals = self._r.zrange(key, 0, -1)
                print(f"Type zset:\n {key} {vals}\n\n")
            if type == b"list":
                vals = self._r.lrange(key, 0, -1)
                print(f"Type list:\n{key} {vals}\n\n")
            if type == b"set":
                vals = self._r.smembers(key)
                print(f"Type set:\n{key} {vals}\n\n")




if __name__ == "__main__":
    db = SwapDB()
    print(db.ping())
    db.dump_all()
