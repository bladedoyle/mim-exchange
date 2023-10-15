#!/usr/bin/env python3 

# CTSwap Main
import os
from decimal import Decimal
import traceback

from flask import Flask, render_template, request, redirect, url_for, session
from forms import ConfigForm, SendLockForm, TrackForm

from db import AdminDB
from lib import wallets
from lib.timestamp import epoch_at, epoch_now

from lib.logger import Logger
from config import get_default_config, get_config_from_form

# Create the Logger
logger = Logger(log_level="INFO")

# XXX TODO
# Ensure config objects exists in the db
config = AdminDB().get_config()
logger.debug("Config {}".format(config))
if len(config) == 0:
    logger.debug("Creating Config")
    default_config = get_default_config()
    AdminDB().set_config(default_config)


# Create the WebUI Front-End
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
app.config["SESSION_COOKIE_NAME"] = "mimexxxchangeadmin"

# Limit decimal places to 6 for display
def shortnumber(value):
    """Shorten long numbers for info display"""
    if value is None:
        return "0.0"
    rounded = round(Decimal(value), 6)
    rounded_str = str(rounded)
    strip = rounded_str.rstrip("0")
    if strip[-1] == ".":
        strip = strip[0:-1]
    return strip

app.jinja_env.filters["shortnumber"] = shortnumber

##
# Define the API / WEBUI Endpoints
@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        tb = traceback.format_exc()
        error_message = f"ERROR: {str(e)} - {tb}"
        logger.error(error_message)
        return render_template('error.html', msg=error_message)


@app.route('/config', methods=['GET', 'POST'])
def config():
    try:
        # Get current config
        default_config = get_default_config()
        config = AdminDB().get_config()
        # Create the form and set current values
        form = ConfigForm()
        if request.method == "POST":
            # Validate the form input / display error status
            if form.validate_on_submit():
                config = get_config_from_form(form)
                AdminDB().set_config(config)
                return render_template('config.html', form=form)
        # method == "GET"
        form.exchange_fee.data = config.get("exchange_fee") or default_config["exchange_fee"]
        form.price_data_expire.data = config.get("price_data_expire") or default_config["price_data_expire"]
        form.exchange_rate_expire.data = config.get("exchange_rate_expire") or default_config["exchange_rate_expire"]
        form.completed_swap_archive.data = config.get("completed_swap_archive") or default_config["completed_swap_archive"]
        form.incomplete_swap_expire.data = config.get("incomplete_swap_expire") or default_config["incomplete_swap_expire"]
        form.archived_swap_delete.data = config.get("archived_swap_delete") or default_config["archived_swap_delete"]
        form.swap_cookie_expire.data = config.get("swap_cookie_expire") or default_config["swap_cookie_expire"]
        form.minimum_swap_value_dollars.data = config.get("minimum_swap_value_dollars") or default_config["minimum_swap_value_dollars"]
        form.maintenance_mode.data = config.get("maintenance_mode") or default_config["maintenance_mode"]
        form.maintenance_list.data = config.get("maintenance_list") or default_config["maintenance_list"]
        form.support_email.data = config.get("support_email") or default_config["support_email"]
        return render_template('config.html', form=form)
    except Exception as e:
        tb = traceback.format_exc()
        error_message = f"ERROR: {str(e)} - {tb}"
        logger.error(error_message)
        return render_template('error.html', msg=error_message)


@app.route('/active_exchanges', methods=['GET'])
def active_exchanges():
    try:
        active = AdminDB().get_active_swaps()
        return render_template('exchanges.html', type="Active", swaps=active)
    except Exception as e:
        tb = traceback.format_exc()
        error_message = f"ERROR: {str(e)} - {tb}"
        logger.error(error_message)
        return render_template('error.html', msg=error_message)


@app.route('/completed_exchanges', methods=['GET'])
def completed_exchanges():
    try:
        completed = AdminDB().get_completed_swaps()
        return render_template('exchanges.html', type="Completed", swaps=completed)
    except Exception as e:
        tb = traceback.format_exc()
        error_message = f"ERROR: {str(e)} - {tb}"
        logger.error(error_message)
        return render_template('error.html', msg=error_message)


@app.route('/lock', methods=['GET', 'POST'])
def lock():
    try:
        lock = AdminDB().get_send_lock()
        form = SendLockForm()
        if request.method == "POST":
            # Validate the form input / display error status
            if form.validate_on_submit():
                lock = len(form.send_lock.raw_data) > 0
                if lock:
                    AdminDB().set_send_lock("admin")
                else:
                    AdminDB().unset_send_lock()
                return render_template('lock.html', form=form)
        form.send_lock.data = lock
        return render_template('lock.html', form=form)
    except Exception as e:
        tb = traceback.format_exc()
        error_message = f"ERROR: {str(e)} - {tb}"
        logger.error(error_message)
        return render_template('error.html', msg=error_message)


@app.route('/swap/<swap_id>', methods=['GET'])
def swap(swap_id):
    swap = AdminDB().get_swap(swap_id)
    if swap is None:
        message = f"Swap not found: {swap_id}"
        return render_template('error.html', msg=message)
    return render_template('swap.html', swap=swap)


@app.route('/track', methods=['GET', 'POST'])
def track():
    try:
        # Create the form
        form = TrackForm()
        if request.method == "POST":
            # Validate the form input / display error status
            if form.validate_on_submit():
                return redirect(url_for('swap', swap_id=form.swap_id.data))
        return render_template('track.html', form=form)
    except Exception as e:
        tb = traceback.format_exc()
        error_message = f"ERROR: {str(e)} - {tb}"
        logger.error(error_message)
        return render_template('error.html', msg=error_message)

# Start from commandline for debugging
if __name__ == "__main__":
    app.run(port=5002)
