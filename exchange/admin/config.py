# Default config

def get_default_config():
    return {
        "exchange_fee":  1,                 # 1% fee
        "price_data_expire": 30,            # 30 minutes
        "exchange_rate_expire": 30,         # 30 Minutes
        "completed_swap_archive": 7,         # 7 Days
        "incomplete_swap_expire": 7,        # 7 Days
        "archived_swap_delete": 30,          # 30 Days
        "swap_cookie_expire": 24,           # Hours
        "minimum_swap_value_dollars": 1,    # 1 Dollar
        "maintenance_mode": False,          # Place entire exchange in maintenance mode
        "maintenance_list": "",             # CSV list of coins in maintenance mode with trading disabled
        "support_email": "mimexchange@proton.me",
    }

def get_config_from_form(form):
    return {
        "exchange_fee":  form.exchange_fee.data,
        "price_data_expire": form.price_data_expire.data,
        "exchange_rate_expire": form.exchange_rate_expire.data,
        "completed_swap_archive": form.completed_swap_archive.data,
        "incomplete_swap_expire": form.incomplete_swap_expire.data,
        "archived_swap_delete": form.archived_swap_delete.data,
        "swap_cookie_expire": form.swap_cookie_expire.data,
        "minimum_swap_value_dollars": form.minimum_swap_value_dollars.data,
        "maintenance_mode": form.maintenance_mode.data,
        "maintenance_list": form.maintenance_list.data,
        "support_email": form.support_email.data,
    }
