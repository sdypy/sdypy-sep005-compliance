import numpy as np

from datetime import datetime

COMPULSORY_FIELDS = ['data','name','unit_str']
PROHIBITED_FIELDS = ['timestamp']

def assert_sep005(timeseries:list):
    """
    Assert the compliance with the SEP005 guidelines as specified in
    https://github.com/sdypy/sdypy/blob/main/docs/seps/sep-0005.rst

    """

    # Check datatype
    if type(timeseries) != list:
        raise TypeError(f'Invalid datatype {type(timeseries)}, should be list')

    # Check the individual channels
    for channel in timeseries:
        assert_sep005_channel(channel)

def assert_sep005_channel(channel:dict):
    """
    Assert the compliance of the individual channels
    """

    if type(channel) != dict:
        raise TypeError(f'Invalid datatype {type(channel)}, should be dict')

    keys = list(channel.keys())

    check_prohibited_fields(keys)
    check_compulsory_fields(keys)

    if 'time' in keys:
        if len(channel['time']) != len(channel['data']):
            raise ValueError(
                f"Length of the time vector and data vector do not match :"
                f" {len(channel['time'])} vs. {len(channel['data'])}")

    check_timestamp_iso8601(channel)

    if type(channel['data']) != np.ndarray:
        raise TypeError(f"Invalid datatype {type(channel['data'])}, should be np.array")

def check_compulsory_fields(keywords:list):
    """
    Check that all the compulsory fields are present
    """

    for c_key in COMPULSORY_FIELDS:
        if c_key not in keywords:
            raise ValueError(f"Missing compulsory keyword '{c_key}'")

    if 'time' not in keywords and 'fs' not in keywords:
        raise ValueError(f"Missing information to replicate time")

def check_prohibited_fields(keywords:list):
    """
    Checks that none of the prohibited fields are included in the channels keywords

    - Check errors in case in the compulsory fields
    - Check if none of the fields are in the forbidden field list
    """

    for key in keywords:
        if key.lower() in [c_key.lower() for c_key in COMPULSORY_FIELDS] and (key not in COMPULSORY_FIELDS):
            for c_key in COMPULSORY_FIELDS:
                if key.lower() == c_key:
                    raise ValueError(f"'{key}' is an invalid keyword, please use '{c_key}' instead.")

    for key in keywords:
        if key.lower() in [p_key.lower() for p_key in PROHIBITED_FIELDS]:
            raise ValueError(f"'{key}' is a Prohibited keyword, do not use it.")

def check_timestamp_iso8601(channel):
    """
    Check that any timestamp provided is in ISO8601
    """
    keys = list(channel.keys())

    for key in keys:
        if 'timestamp' in key:
            dt_str = channel[key]
            try:
                datetime.fromisoformat(dt_str)
            except:
                raise TypeError(f"Timestamp '{key}':{dt_str} is not according to ISO8601")
