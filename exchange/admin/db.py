import redis
import json

class AdminDB:
    def __init__(self):
        self._r = redis.Redis(host='redis', port=6379, db=0)
        self._r.ping()

    # Write one or more app configuration values 
    def set_config(self, config):
        key = "config"
        value = json.dumps(config)
        self._r.set(key, value)

    # Get app configuration
    def get_config(self):
        key = "config"
        value = self._r.get(key)
        return json.loads(value.decode()) if value is not None else {}

    # Get swap
    def get_swap(self, id):
        # Try active swaps
        name = "swaps"
        value = self._r.hget(name, id)
        if value is None:
            # Try completed swaps
            name = "completed_swaps"
            value = self._r.hget(name, id)
        if value is not None:
            value = json.loads(value.decode())
        return value

    # Delete a swap
    def del_swap(self, id):
        name = "swaps"
        self._r.hdel(name, id)

    # Get all active swaps
    def get_active_swaps(self):
        name = "swaps"
        values = self._r.hgetall(name)
        return {k.decode(): json.loads(v.decode()) for k, v in values.items()}

    # Get all completed swaps
    def get_completed_swaps(self):
        name = "completed_swaps"
        values = self._r.hgetall(name)
        return {k.decode(): json.loads(v.decode()) for k, v in values.items()}

    # Get TX fees data
    def get_tx_fees(self):
        key = "tx_fees"
        value = self._r.get(key)
        if value is None:
            return None
        return json.loads(value.decode())

    # send lock
    def get_send_lock(self):
        key = "send_lock"
        value = self._r.get(key)
        if value == None:
            return None
        return json.loads(value.decode())

    def set_send_lock(self, swap_id):
        key = "send_lock"
        value = json.dumps(swap_id)
        self._r.set(key, value)

    def unset_send_lock(self):
        key = "send_lock"
        self._r.delete(key)