from datetime import datetime, timezone

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
    assert channel.data == [1, 2, 3]
    assert channel.time == [1, 2, 3]


def test_prohibited_keywords():
    with pytest.raises(
        ValidationError, match="'timestamp' is a Prohibited keyword"
    ):
        Sep005Data.model_validate(
            valid_channel(timestamp="2025-01-01T00:00:00")
        )

    for bad_key in ("Unit_Str",):
        with pytest.raises(
            ValidationError,
            match=f"'{bad_key}' is an invalid keyword",
        ):
            Sep005Data.model_validate(valid_channel(**{bad_key: "m"}))


def test_compulsory_keywords():
    with pytest.raises(ValidationError):
        Sep005Data.model_validate(
            {"name": "test", "unit_str": "m", "data": [1]}
        )

    Sep005Data.model_validate(
        {"name": "test", "unit_str": "m", "data": [1], "fs": 100.0}
    )

    for field in ("data", "name", "unit_str"):
        payload = valid_channel(fs=100.0)
        del payload[field]
        with pytest.raises(ValidationError):
            Sep005Data.model_validate(payload)


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


def test_invalid_input_type():
    with pytest.raises(ValidationError):
        Sep005Data.model_validate("Not SEP005 compliant")


def test_timestamps():
    Sep005Data.model_validate(
        valid_channel(start_timestamp=str(datetime.now(timezone.utc)))  # noqa: UP017
    )

    with pytest.raises(ValidationError, match="end_timestamp"):
        Sep005Data.model_validate(
            valid_channel(
                start_timestamp=str(datetime.now(timezone.utc)),  # noqa: UP017
                end_timestamp="2023/08/23 1200",
            )
        )


def test_unknown_extra_field_allowed():
    channel = Sep005Data.model_validate(valid_channel(unknown_field="value"))
    assert channel.__pydantic_extra__ == {"unknown_field": "value"}
