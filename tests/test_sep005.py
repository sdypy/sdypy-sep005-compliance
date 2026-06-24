import math
from datetime import datetime, timezone

import numpy as np
import pytest
from pydantic import ValidationError

import sdypy_sep005
from sdypy_sep005 import Sep005Data


def valid_channel(**overrides):
    channel = {
        "name": "test",
        "unit_str": "m",
        "data": [1, 2, 3],
        "time": [1, 2, 3],
    }
    channel.update(overrides)
    return channel


def test_version():
    """Check sdypy_sep005 exposes a version attribute."""
    assert hasattr(sdypy_sep005, "__version__")
    assert isinstance(sdypy_sep005.__version__, str)


def test_valid_channel():
    channel = Sep005Data.model_validate(valid_channel())
    assert channel.name == "test"
    assert channel.data == [1.0, 2.0, 3.0]
    assert channel.time == [1, 2, 3]


def test_data_accepts_missing_samples():
    channel = Sep005Data.model_validate(
        valid_channel(data=[1, None, float("nan")])
    )
    assert channel.data[0] == 1.0
    assert channel.data[1] is None
    assert math.isnan(channel.data[2])


def test_data_accepts_numpy_array():
    data = np.array([1, 2, 3], dtype=np.int64)
    channel = Sep005Data.model_validate(valid_channel(data=data))
    assert isinstance(channel.data, np.ndarray)
    np.testing.assert_array_equal(channel.data, data)
    assert channel.data.dtype == np.int64


@pytest.mark.parametrize(
    "bad_key,expected_key",
    [
        ("Data", "data"),
        ("Name", "name"),
        ("Unit_Str", "unit_str"),
        ("Time", "time"),
        ("Fs", "fs"),
        ("Quantity", "quantity"),
        ("Unit_Tex", "unit_tex"),
        ("Start_Timestamp", "start_timestamp"),
        ("End_Timestamp", "end_timestamp"),
        ("Group", "group"),
    ],
)
def test_field_names_are_case_sensitive(bad_key, expected_key):
    with pytest.raises(
        ValidationError,
        match=f"'{bad_key}' is an invalid keyword, please use '{expected_key}'",
    ):
        Sep005Data.model_validate(valid_channel(**{bad_key: "extra"}))


@pytest.mark.parametrize("bad_key", ["timestamp", "Timestamp", "TIMESTAMP"])
def test_prohibited_keyword_is_case_insensitive(bad_key):
    with pytest.raises(
        ValidationError, match=f"'{bad_key}' is a Prohibited keyword"
    ):
        Sep005Data.model_validate(valid_channel(**{bad_key: "2025-01-01"}))


def test_compulsory_keywords():
    with pytest.raises(ValidationError):
        Sep005Data.model_validate(
            {"name": "test", "unit_str": "m", "data": [1]}
        )

    for field in ("data", "name", "unit_str"):
        payload = valid_channel(fs=100.0)
        del payload[field]
        with pytest.raises(ValidationError):
            Sep005Data.model_validate(payload)


def test_data_accepts_list():
    channel = Sep005Data.model_validate(valid_channel(data=[1, 2, 3]))
    assert isinstance(channel.data, list)
    assert channel.data == [1.0, 2.0, 3.0]


def test_empty_time_and_data_vectors_are_valid():
    channel = Sep005Data.model_validate(valid_channel(data=[], time=[]))
    assert channel.data == []
    assert channel.time == []


def test_time_information_required():
    with pytest.raises(
        ValidationError, match="Must provide either 'time' or 'fs'"
    ):
        Sep005Data.model_validate(
            {"name": "test", "unit_str": "m", "data": [1, 2, 3]}
        )


def test_time_length_matches_data():
    with pytest.raises(
        ValidationError,
        match="Length of time vector \\(2\\) must match data vector"
        " length \\(3\\)",
    ):
        Sep005Data.model_validate(valid_channel(time=[1, 3]))


def test_time_length_validation_allows_fs_without_time():
    channel = Sep005Data.model_validate(valid_channel(time=None, fs=100.0))
    assert channel.time is None
    assert channel.fs == 100.0


@pytest.mark.parametrize(
    "payload",
    [
        None,
        "Not SEP005 compliant",
        ["name", "unit_str", "data", "time"],
        42,
    ],
)
def test_invalid_input_types(payload):
    with pytest.raises(ValidationError):
        Sep005Data.model_validate(payload)


@pytest.mark.parametrize(
    "timestamp",
    [
        "2025-08-16T01:00:00",
        "2025-08-16T01:00:00+00:00",
        "2025-08-16T01:00:00Z",
        str(datetime.now(timezone.utc)),  # noqa: UP017
    ],
)
def test_valid_timestamps(timestamp):
    Sep005Data.model_validate(valid_channel(start_timestamp=timestamp))


@pytest.mark.parametrize(
    "field_name",
    ["start_timestamp", "end_timestamp"],
)
def test_timestamps_accept_datetime_objects(field_name):
    timestamp = datetime(2023, 11, 15, 12, tzinfo=timezone.utc)  # noqa: UP017
    channel = Sep005Data.model_validate(
        valid_channel(**{field_name: timestamp})
    )
    assert getattr(channel, field_name) == timestamp.isoformat()


@pytest.mark.parametrize(
    "field_name",
    ["start_timestamp", "end_timestamp"],
)
def test_invalid_timestamps_report_field_name(field_name):
    with pytest.raises(ValidationError, match=field_name):
        Sep005Data.model_validate(
            valid_channel(**{field_name: "2023/08/23 1200"})
        )


def test_unknown_extra_fields_allowed():
    channel = Sep005Data.model_validate(
        valid_channel(location="tower", sensor_id=42)
    )
    assert channel.__pydantic_extra__ == {
        "location": "tower",
        "sensor_id": 42,
    }
