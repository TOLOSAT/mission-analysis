import pandas
import datetime
import numpy as np
from astropy.time import Time, TimeDelta

J2000 = Time("J2000.0", format="jyear_str", scale="utc")


def datetime_to_epoch_raw(datetime_object):
    astrotime = Time(datetime_object, scale="utc")
    return astrotime_to_epoch_raw(astrotime)


def datetime_to_epoch(datetime_object):
    astrotime = Time(datetime_object, scale="utc")
    if isinstance(datetime_object, datetime.datetime):
        return astrotime_to_epoch_raw(astrotime)
    elif isinstance(datetime_object, list):
        return astrotime_to_epoch_raw(astrotime)
    elif isinstance(datetime_object, np.ndarray):
        return astrotime_to_epoch_raw(astrotime)
    elif isinstance(datetime_object, dict):
        return {key: datetime_to_epoch_raw(dt) for key, dt in datetime_object.items()}
    elif isinstance(datetime_object, pandas.Series) or isinstance(
        datetime_object, pandas.DataFrame
    ):
        return datetime_object.apply(datetime_to_epoch_raw)


def epoch_to_datetime_raw(epoch):
    astrotime = epoch_to_astrotime_raw(epoch)
    dt = astrotime.datetime.replace(tzinfo=datetime.timezone.utc)
    return dt


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
    return J2000 + TimeDelta(epoch, format="sec")


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


def astrotime_to_epoch_raw(astrotime):
    return (astrotime - J2000).sec


def astrotime_to_epoch(astrotime):
    if isinstance(astrotime, Time):
        return astrotime_to_epoch_raw(astrotime)
    elif isinstance(astrotime, list):
        return [astrotime_to_epoch_raw(at) for at in astrotime]
    elif isinstance(astrotime, np.ndarray):
        return np.array(astrotime_to_epoch(astrotime.tolist()))
    elif isinstance(astrotime, dict):
        return {key: astrotime_to_epoch_raw(at) for key, at in astrotime.items()}
    elif isinstance(astrotime, pandas.Series) or isinstance(
        astrotime, pandas.DataFrame
    ):
        return astrotime.apply(astrotime_to_epoch_raw)
