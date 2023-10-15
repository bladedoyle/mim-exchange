from datetime import datetime, timedelta
from pytz import timezone

def epoch_now():
    return epoch_at(datetime.utcnow())

def epoch_at(thetime):
    if type(thetime) == float:
        thetime = datetime.fromtimestamp(thetime)
    return (thetime - datetime(1970, 1, 1)).total_seconds()

def epoch_to_string(epoch):
    tz = timezone('UTC')
    return datetime.fromtimestamp(epoch, tz).strftime('%Y-%m-%d %H:%M:%S')


if __name__ == "__main__":
    # Test
    now = epoch_now()
    print(now)
    str_from_epoch = epoch_to_string(now)
    print(str_from_epoch)
    epoch_later = epoch_at(datetime.utcnow() + timedelta(minutes=10))
    print(epoch_later)
    str_from_epoch_later = epoch_to_string(epoch_later)
    print(str_from_epoch_later)