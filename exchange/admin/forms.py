from flask_wtf import FlaskForm
from wtforms import StringField, validators, BooleanField


##
# Define the WTForms

class ConfigForm(FlaskForm):
    exchange_fee = StringField(
        label=u'Exchange Fee (percent)',
        validators=[validators.InputRequired(),],
    )
    price_data_expire = StringField(
        label=u'Price Data Expire (minutes)',
        validators=[validators.InputRequired(),],
    )
    exchange_rate_expire = StringField(
        label=u'Exchange Rate Expire (minutes)',
        validators=[validators.InputRequired(),],
    )
    completed_swap_archive = StringField(
        label=u'Archive Completed Swaps After (Days)',
        validators=[validators.InputRequired(),],
    )
    incomplete_swap_expire = StringField(
        label=u'Delete Incomplete Swaps After (Days)',
        validators=[validators.InputRequired(),],
    )
    archived_swap_delete = StringField(
        label=u'Delete Incomplete Swaps After (Days)',
        validators=[validators.InputRequired(),],
    )
    swap_cookie_expire = StringField(
        label=u'Expire Swap Cookie (Hours)',
        validators=[validators.InputRequired(),],
    )
    minimum_swap_value_dollars = StringField(
        label=u'Minimum Swap Value (Dollars)',
        validators=[validators.InputRequired(),],
    )
    maintenance_mode = StringField(
        label=u'Exchange is in maintenance mode',
        validators=[validators.InputRequired(),],
    )
    maintenance_list = StringField(
        label=u'Coins in maintenance',
        validators=[],
    )
    support_email = StringField(
        label=u'Support Email Address',
        validators=[validators.InputRequired(),],
    )

class SendLockForm(FlaskForm):
    send_lock = BooleanField(
        label=u'Send Lock',
    )

class TrackForm(FlaskForm):
    swap_id = StringField(
        label=u'Exchange ID',
    )