import re
from decimal import *
from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, StringField, validators, ValidationError

from lib.addresses import is_valid
from lib.utils import decimal_to_string
from db import SwapDB

##
# Define the WTForms

class ChooseForm(FlaskForm):
    swap_from = SelectField(
        label=u'From',
        choices=[
            ('btc', 'BTC'),
            ('xmr', 'XMR'),
            ('bch', 'BCH'),
            ('dash', 'DASH'),
            ('doge', 'DOGE'),
            ('ltc', 'LTC'),
            ('wow', 'WOW'),
            ('zec', 'ZEC'),
        ],
        default="btc",
        validators=[validators.InputRequired(),],
    )
    swap_to = SelectField(
        label=u'To',
        choices=[
            ('btc', 'BTC'),
            ('xmr', 'XMR'),
            ('bch', 'BCH'),
            ('dash', 'DASH'),
            ('doge', 'DOGE'),
            ('ltc', 'LTC'),
            ('wow', 'WOW'),
            ('zec', 'ZEC'),
        ],
        default="xmr",
        validators=[validators.InputRequired(),],
    )
    amount = DecimalField(
        label=u'Amount',
        render_kw={"placeholder": 0.0, "step":"0.000001"},
        places=8,
        validators=[validators.InputRequired(),],
    )

    def __init__(self, *args, **kwargs):
        super(ChooseForm, self).__init__(*args, **kwargs)
        maintenance = SwapDB().get_config()["maintenance_list"].split(",")
        broken = SwapDB().get_broken()
        remove = list(set(maintenance + broken))
        for coin in remove:
            if coin == '':
                continue
            item = (coin, coin.upper())
            self.swap_from.choices.remove(item)
            self.swap_to.choices.remove(item)
        self.swap_from.default=self.swap_from.choices[0][0]
        self.swap_to.default=self.swap_to.choices[1][0]

    def validate_amount(form, field):
        if form.data["amount"] is None:
            # Empty and non-decimal values handled by the built-in validators
            return
        # Check that amount is non-negetive
        swap_from_amount = form.data["amount"]
        if swap_from_amount < 0.0:
            raise ValidationError('Amount must be a positive number')
        # Check that the swap is above minimum usd amount
        swap_from_usd_pair = f"{form.swap_from.data}-usd"
        swap_from_usd_ratio = SwapDB().get_prices()[swap_from_usd_pair]
        minimum_usd_value = Decimal(SwapDB().get_config()["minimum_swap_value_dollars"])
        swap_from_usd_value = swap_from_amount*Decimal(swap_from_usd_ratio)
        if swap_from_usd_value < minimum_usd_value:
            swap_from_min = Decimal(minimum_usd_value)/Decimal(swap_from_usd_ratio)
            raise ValidationError("Amount is below minimum {}".format(decimal_to_string(swap_from_min)))
        # Check that we have enough liquidy
        balances = SwapDB().get_balances()
        if balances is None:
            raise ValidationError("Exchange is paused for maintenance, please try later")
        pair = f"{form.swap_from.data}-{form.swap_to.data}"
        price_ratio = SwapDB().get_prices()[pair]
        if price_ratio is None:
            raise ValidationError(f"Price data for {form.swap_from.data}-{form.swap_to.data} is unavailable, please try later")
        swap_to_max = Decimal(balances[form.swap_to.data]["available"])*Decimal(.97)
        amount_swap_to = swap_from_amount*Decimal(price_ratio)
        if amount_swap_to > swap_to_max:
            swap_from_max = decimal_to_string(Decimal(swap_to_max)*Decimal(.97)/Decimal(price_ratio))
            raise ValidationError(f'Amount exceedes current liquidity.  Max {form.swap_from.data} that can be sent is {swap_from_max}')

    def validate_swap_to(form, field):
        if form.swap_to.data is None:
            raise ValidationError('Must choose a coin to exchange to')
        if form.swap_to.data == form.swap_from.data:
            raise ValidationError(f'Can not convert {form.swap_from.data} to {form.swap_to.data}')
        if form.swap_to.data in SwapDB().get_config()["maintenance_list"].split(","):
            raise ValidationError(f'Exchange of {form.swap_to.data} is disabled for maintenance')
        
    def validate_swap_from(form, field):
        in_maintenance = SwapDB().get_config()["maintenance_list"].split(",")
        if form.swap_from.data in in_maintenance:
            raise ValidationError(f'Exchange of {form.swap_from.data} is disabled for maintenance')


class AddressForm(FlaskForm):
    swap_to_address = StringField(
        label=u'',
        validators=[validators.InputRequired(),],
    )
    captcha = StringField(
        label=u'Solve Captcha',
        validators=[validators.InputRequired(),],
    )

    def filter_swap_to_address(form, field):
        if field is not None:
            return field.strip()
        else:
            return field

    def validate_swap_to_address(form, field):
        valid = is_valid(form.swap_to, field.data)
        if valid is None or valid == False:
             raise ValidationError(f'Invalid {form.swap_to} address')
    
    def validate_captcha(form, field):
        if form.captcha_solution != field.data:
            raise ValidationError(f'Invalid Captcha Solution')


class RefundAddressForm(FlaskForm):
    refund_address = StringField(
        label=u'',
        validators=[validators.InputRequired(),],
    )
    
    def filter_refund_address(form, field):
        if field is not None:
            return field.strip()
        else:
            return field
    
    def validate_refund_address(form, field):
        valid = is_valid(form.swap_from, field.data.strip())
        if valid is None or valid == False:
             raise ValidationError(f'Invalid {form.swap_from} address')


class TrackForm(FlaskForm):
    swap_id = StringField(
        label=u'',
        validators=[validators.InputRequired(),],
    )
    captcha = StringField(
        label=u'Solve Captcha',
        validators=[validators.InputRequired(),],
    )

    def validate_swap_id(form, field):
        valid = True
        if re.fullmatch(r"^[0-9a-f]{12}$", field.data or "") is None:
            valid = False
        swap = SwapDB().get_swap(field.data)
        if swap is None:
            valid = False
        if not valid:
             raise ValidationError(f'Invalid Swap ID')

    def validate_captcha(form, field):
        if form.captcha_solution != field.data:
            raise ValidationError(f'Invalid Captcha Solution')