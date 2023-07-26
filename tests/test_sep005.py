import pytest
import sdypy_sep005

import numpy as np

from datetime import datetime

# Pytest will discover and run all test functions named `test_*` or `*_test`.

def test_version():
    """ check sdypy_template_project exposes a version attribute """
    assert hasattr(sdypy_sep005, "__version__")
    assert isinstance(sdypy_sep005.__version__, str)


def test_prohibited_keywords():
    from sdypy_sep005.sep005 import check_prohibited_fields

    with pytest.raises(ValueError, match="'timestamp' is a Prohibited keyword"):
        check_prohibited_fields(['timestamp'])

    for bad_key in ['Unit_Str']:
        with pytest.raises(ValueError, match=f"'{bad_key}' is an invalid keyword"):
            check_prohibited_fields([bad_key])

def test_compulsory_keywords():
    import copy
    import random

    from sdypy_sep005.sep005 import check_compulsory_fields
    from sdypy_sep005.sep005 import COMPULSORY_FIELDS

    # Shouldn't pass as time info is missing
    with pytest.raises(ValueError):
        check_compulsory_fields(COMPULSORY_FIELDS)

    comp_list = copy.copy(COMPULSORY_FIELDS)
    comp_list.append('fs')
    check_compulsory_fields(comp_list) # Should pass

    # Remove random element, shouldn't pass
    random_element = random.choice(COMPULSORY_FIELDS)
    comp_list.remove(random_element)
    with pytest.raises(ValueError):
        check_compulsory_fields(comp_list)

def test_assert_sep005():
    from sdypy_sep005.sep005 import assert_sep005

    dummy_channels = [
        {
            'name' : 'test',
            'unit_str': 'm',
            'data': np.array([1,2,3]),
            'time': np.array([1,2,3])
        }
    ]

    assert_sep005(dummy_channels)

    #
    dummy_channels.append(
        {
            'name': 'test',
            'unit_str': 'm',
            'data': np.array([1, 2, 3]),
            'time': np.array([1, 3])
        }
    )

    with pytest.raises(ValueError, match= 'Length of the time vector and data vector do not match'):
        assert_sep005(dummy_channels)

    # Type errors
    with pytest.raises(TypeError):
        assert_sep005('Not SEP005 compliant')   # string

    with pytest.raises(TypeError):
        assert_sep005([[]]) # Channel should be dict, not list

def test_timestamps():
    from sdypy_sep005.sep005 import check_timestamp_iso8601

    check_timestamp_iso8601(
        {'start_timestamp':str(datetime.utcnow())}
    )
    with pytest.raises(TypeError, match="end_timestamp"):
        check_timestamp_iso8601(
            {
                'start_timestamp': str(datetime.utcnow()),
                'end_timestamp': '2023/08/23 1200',
             }
        )