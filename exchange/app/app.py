#!/usr/bin/env python3 

# Exchange Main
from datetime import datetime, timedelta
import traceback

from flask import Flask, render_template, request, redirect, url_for, session
from forms import ChooseForm, AddressForm, RefundAddressForm, TrackForm
from jinja2.runtime import Undefined

from db import SwapDB
from lib import addresses, utils
import exchange
from lib.swap import Swap
from lib.timestamp import epoch_to_string, epoch_at
from lib.logger import Logger

# Create the Logger
logger = Logger(log_level="INFO")

# Create the WebUI Front-End
app = Flask(__name__)
app.config['SECRET_KEY'] = b'\x1b\xc1(\xcb\x8e\x9a\xcb\xa4"\xa4.D\xeeK\xd2\x9a\x18S\xa8\x81\x91WQ8\xeb\xf44\xee\xb8\x10\x925' # os.urandom(32)
app.config["SESSION_COOKIE_NAME"] = "mimexchange"


##
# Add some custom jinja filters

# Shorten long addresses for progress bar display
def shortaddress(value):
    """Shorten long addresses for info display"""
    if value is None:
        return ""
    return addresses.shorten(value, 32)
app.jinja_env.filters["shortaddress"] = shortaddress

# Limit decimal places to 6 for display
def shortnumber(value, precision=6):
    """Shorten long numbers for info display"""
    if value is None or type(value) is Undefined:
        return "?.??"
    return utils.decimal_to_string(value, precision)
app.jinja_env.filters["shortnumber"] = shortnumber

# Format dates without milliseconds for disaply
def timestamp(value):
    """Format timestamps for disaply"""
    return epoch_to_string(value)
app.jinja_env.filters["timestamp"] = timestamp


##
# Various criteria for disabling the entire exchange
def in_maintenance():
    if SwapDB().get_config()["maintenance_mode"] == True:
        logger.warning(f"Maintenance Mode set in Config")
        return True
    if SwapDB().get_exchange_heartbeat() < epoch_at(datetime.utcnow() - timedelta(minutes=10)):
        logger.warning(f"Exchange heartbeat is expired")
        return True


##
# Define the API / WEBUI Endpoints
@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if in_maintenance() == True:
            return render_template('maintenance.html')
        # Create the form
        form = ChooseForm()
        if request.method == "POST":
            # Once address is set we dont show this form again
            if "swap" in session and (session["swap"]["swap_to_address"] is not None or SwapDB().get_swap(session["swap"]["id"]) is not None):
                # Go to the swap page
                return redirect(url_for('swap', swap_id=session["swap"]["id"]))
            # Validate the form input / display error status
            if form.validate_on_submit():
                # Validates OK, Create a swap and save the form data in the users session
                swap = Swap()
                swap.swap_from = form.swap_from.data
                swap.swap_to = form.swap_to.data
                swap.quoted_swap_from_amount = form.amount.data
                exchange.calculate_swap(swap)
                session["swap"] = swap.dict()
                session.modified = True
                # Go to the next page
                return redirect(url_for('address'))
        # method == "GET"
        # Begin a new Swap Session
        session.pop("swap", None)
        # Get current market
        market = SwapDB().get_prices()
        # Get current liquidity
        liquidity = SwapDB().get_balances()
        # Get broken/maintenance coins
        broken = SwapDB().get_broken()
        maintenance = SwapDB().get_config()["maintenance_list"].split(",")
        offline = list(set(broken + maintenance))
        return render_template('index.html', form=form, market=market, liquidity=liquidity, offline=offline)
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"ERROR: {str(e)} - {tb}")
        return render_template('maintenance.html')


@app.route('/address', methods=['GET', 'POST'])
def address():
    try:
        if in_maintenance() == True:
            return render_template('maintenance.html')
        # Make sure they choose coins first
        if not "swap" in session:
            # Go back to choose form
            return redirect(url_for('index'))
        swap = Swap(session["swap"])
        # Once address is set we dont show this form again
        if swap.swap_to_address is not None or SwapDB().get_swap(swap.id) is not None:
            # Go to the swap page
            return redirect(url_for('swap', swap_id=swap.id))
        # Create the form
        form = AddressForm()
        form.swap_to = swap.swap_to
        if request.method == "POST" and swap.swap_to_address is None:
            # Validate the form input / display error status
            if "captcha_solution" in session:
                form.captcha_solution = session["captcha_solution"]
            if form.validate_on_submit():
                # Validates OK, save the form data in the users session
                swap.swap_to_address = form.swap_to_address.data
                # Get a swap_from_address and qr
                if swap.swap_from_address is None:
                    (swap.swap_from_address, swap.send_from_address) = addresses.get_new(swap.swap_from)
                # Save to database
                SwapDB().set_swap(swap)
                # Set cookie and Go to the next page
                response = redirect(url_for('swap', swap_id=swap.id))
                expires = timedelta(days=1).total_seconds()
                response.set_cookie(swap.id, swap.id, max_age=expires)
                return response
        # Create a captcha challenge
        captcha = utils.get_captcha()
        session["captcha_solution"] = captcha["solution"]
        session.modified = True
        # Calculate Exchange Data
        exchange.calculate_swap(swap)
        return render_template('address.html', form=form, swap=swap.dict(), captcha_img=captcha["image"])
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"ERROR: {str(e)} - {tb}")
        return render_template('maintenance.html')


@app.route('/swap/<swap_id>', methods=['GET', 'POST'])
def swap(swap_id):
    try:
        if in_maintenance() == True:
            return render_template('maintenance.html')
        if not request.cookies.get(swap_id) == swap_id:
            # Go back to choose form
            return redirect(url_for('index'))
        # Get swap status from the database
        swap = SwapDB().get_swap(swap_id)
        if swap is None:
            # This swap is so old it was deleted and is no longer active
            return redirect(url_for('index'))
        if swap.recvd_from == False:
            exchange.calculate_swap(swap)
        # Create the refund address form
        form = RefundAddressForm()
        form.swap_from = swap.swap_from
        if request.method == "POST" and swap.refund_address is None:
            # Validate the refund address form input / display error status
            if form.validate_on_submit():
                # Validates OK, save the form data in the users session
                swap.refund_address = form.refund_address.data
                SwapDB().set_swap(swap)
        # Generate the swap_from_address qr if we didnt recv the coins yet
        if swap.recvd_from == False:
            qr = addresses.get_qrcode(swap.swap_from, swap.swap_from_address)
        else:
            qr = None
        return render_template('swap.html', swap=swap.dict(), swap_from_address_qr=qr, form=form)
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"ERROR: {str(e)} - {tb}")
        return render_template('maintenance.html')


@app.route('/track', methods=['GET', 'POST'])
def track():
    try:
        if in_maintenance() == True:
            return render_template('maintenance.html')
        # Begin a new Swap Session
        session.pop("swap", None)
        # Create the form
        form = TrackForm()
        if request.method == "POST":
            # Validate the form input / display error status
            if "captcha_solution" in session:
                form.captcha_solution = session["captcha_solution"]
                if form.validate_on_submit():
                    # Validates OK, save the form data in a cookie
                    response = redirect(url_for('swap', swap_id=form.swap_id.data))
                    expires = timedelta(days=1).total_seconds()
                    response.set_cookie(form.swap_id.data, form.swap_id.data, max_age=expires)
                    return response
        # Create a captcha challenge
        captcha = utils.get_captcha()
        session["captcha_solution"] = captcha["solution"]
        session.modified = True
        return render_template('track.html', form=form, captcha_img=captcha["image"])
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"ERROR: {str(e)} - {tb}")
        return render_template('maintenance.html')


@app.route('/support', methods=['GET'])
def support():
    try:
        config = SwapDB().get_config()
        cfg = {
            "exchange_fee": config["exchange_fee"],
            "completed_swap_archive": config["completed_swap_archive"],
            "incomplete_swap_expire": config["incomplete_swap_expire"],
            "exchange_rate_expire": config["exchange_rate_expire"],
            "support_email": config["support_email"],
            "minimum_swap_value_dollars": config["minimum_swap_value_dollars"],
        }
        return render_template('support.html', cfg=cfg)
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"ERROR: {str(e)} - {tb}")
        return render_template('maintenance.html')


# Start from commandline for debugging
if __name__ == "__main__":
    app.run(port=5001)