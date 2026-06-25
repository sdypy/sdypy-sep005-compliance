# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.4
#   kernelspec:
#     display_name: .venv
#     language: python
#     name: python3
# ---

# %% [markdown]
# # SEP-005 model validation demo
#
# Convert Python dicts into `Sep005Data` with `model_validate`.

# %%
from pydantic import ValidationError

from sdypy_sep005 import Sep005Data

# %% [markdown]
# ## Valid channel with a time vector

# %%
channel = {
    "name": "Tower acceleration",
    "unit_str": "m/s²",
    "data": [1.5, 2.3, None, 2.1],
    "time": [0.0, 0.01, 0.02, 0.03],
    "quantity": "a",
    "group": "tower",
}

model = Sep005Data.model_validate(channel)
model

# %%
model.model_dump()

# %% [markdown]
# ## Valid channel with sampling frequency instead of time

# %%
channel_fs = {
    "name": "Rotor speed",
    "unit_str": "rpm",
    "data": [12.1, 12.3, 12.0],
    "fs": 100.0,
    "start_timestamp": "2025-08-16T01:00:00Z",
    "end_timestamp": "2025-08-16T01:00:08+00:00",
}

Sep005Data.model_validate(channel_fs)

# %% [markdown]
# ## Extra fields are kept in `__pydantic_extra__`

# %%
channel_with_extra = {
    **channel,
    "sensor_id": 42,
    "location": "tower-top",
}

model_with_extra = Sep005Data.model_validate(channel_with_extra)
model_with_extra.__pydantic_extra__

# %% [markdown]
# ## Validation errors

# %%
invalid_cases = [
    {"name": "x", "unit_str": "m", "data": [1, 2, 3]},  # missing time/fs
    {
        "name": "x",
        "unit_str": "m",
        "data": [1, 2, 3],
        "time": [0.0, 0.1],
    },  # time length mismatch
    {
        **channel,
        "timestamp": "2025-01-01T00:00:00",
    },  # prohibited field
    {
        **channel,
        "Unit_Str": "m/s²",
    },  # wrong field casing
]

for payload in invalid_cases:
    print("-" * 60)
    try:
        Sep005Data.model_validate(payload)
    except ValidationError as exc:
        print(exc.errors()[0]["msg"])
