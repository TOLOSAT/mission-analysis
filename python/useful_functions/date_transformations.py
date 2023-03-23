import pandas
from tudatpy.kernel.astro import time_conversion
import datetime
import numpy as np
from astropy.time import Time, TimeDelta

J2000 = Time("J2000.0", format="jyear_str", scale="utc")


def datetime_to_epoch_raw(datetime_object):
    return time_conversion.julian_day_to_seconds_since_epoch(
        time_conversion.calendar_date_to_julian_day(datetime_object)
    )


def datetime_to_epoch(datetime_object):
    if isinstance(datetime_object, datetime.datetime):
        return datetime_to_epoch_raw(datetime_object)
    elif isinstance(datetime_object, list):
        return [datetime_to_epoch_raw(dt) for dt in datetime_object]
    elif isinstance(datetime_object, dict):
        return {key: datetime_to_epoch_raw(dt) for key, dt in datetime_object.items()}
    elif isinstance(datetime_object, pandas.Series) or isinstance(
        datetime_object, pandas.DataFrame
    ):
        return datetime_object.apply(datetime_to_epoch_raw)


def epoch_to_datetime_raw(epoch):
    return time_conversion.julian_day_to_calendar_date(
        time_conversion.seconds_since_epoch_to_julian_day(epoch)
    ).replace(tzinfo=datetime.timezone.utc)


def epoch_to_datetime(epoch):
    if isinstance(epoch, float) or isinstance(epoch, int):
        return epoch_to_datetime_raw(epoch)
    elif isinstance(epoch, list):
        return [epoch_to_datetime_raw(ep) for ep in epoch]
    elif isinstance(epoch, np.ndarray):
        return np.array(epoch_to_datetime(epoch.tolist()))
    elif isinstance(epoch, dict):
        return {key: epoch_to_datetime_raw(ep) for key, ep in epoch.items()}
    elif isinstance(epoch, pandas.Series) or isinstance(epoch, pandas.DataFrame):
        return epoch.apply(epoch_to_datetime_raw)


def epoch_to_astrotime_raw(epoch):
    timedelta = TimeDelta(epoch, format="sec")
    return J2000 + timedelta


def epoch_to_astrotime(epoch):
    if isinstance(epoch, float) or isinstance(epoch, int):
        return epoch_to_astrotime_raw(epoch)
    elif isinstance(epoch, list):
        return [epoch_to_astrotime_raw(ep) for ep in epoch]
    elif isinstance(epoch, np.ndarray):
        return np.array(epoch_to_astrotime(epoch.tolist()))
    elif isinstance(epoch, dict):
        return {key: epoch_to_astrotime_raw(ep) for key, ep in epoch.items()}
    elif isinstance(epoch, pandas.Series) or isinstance(epoch, pandas.DataFrame):
        return epoch.apply(epoch_to_astrotime_raw)
