from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


PROHIBITED_FIELDS = ["timestamp"]


class Sep005Data(BaseModel):  # pylint: disable=R0903
    """SEP-005 pydantinc model used to validate the data against the
    SEP-005 guidelines.
    """

    # Compulsory fields per SEP-005
    data: list[Optional[float]] = Field(  # noqa: UP045
        ..., description="1D array of measurement values"
    )

    name: str = Field(
        ..., description="Descriptive name of the timeseries/channel"
    )
    unit_str: str = Field(
        ...,
        description="Physical unit of the measurement"
        " (e.g., _m/s²_, _kN_, _°C_)",
    )

    # Time information (at least one required per SEP-005)
    time: Optional[list[float]] = Field(  # noqa: UP045
        None, description="Time vector in seconds (optional if fs is provided)"
    )
    fs: Optional[float] = Field(  # noqa: UP045
        None,
        description="Sampling frequency in Hz (optional if time is provided)",
    )

    # Optional fields per SEP-005
    quantity: Optional[str] = Field(  # noqa: UP045
        None,
        description=(
            "Physical quantity type - 'f' (force), 'a' (acceleration), 'v'"
            " (velocity), 'd' (displacement), 'e' (strain), 's' (stress)"
        ),
    )
    unit_tex: Optional[str] = Field(  # noqa: UP045
        None, description="LaTeX representation of unit_str (e.g., 'm/s$^2$')"
    )
    start_timestamp: Optional[str] = Field(  # noqa: UP045
        None, description="ISO 8601 timestamp of first sample"
    )
    end_timestamp: Optional[str] = Field(  # noqa: UP045
        None, description="ISO 8601 timestamp of last sample"
    )
    group: Optional[str] = Field(  # noqa: UP045
        None, description="Group of the timeseries/channel"
    )

    @model_validator(mode="after")
    def validate_sep005_compliance(self):
        """Validate complete SEP-005 compliance.

        Checks:
        1. Either 'time' or 'fs' must be provided
        2. If 'time' is provided, length must match 'data' length
        3. All *_timestamp fields must be valid ISO 8601 format
        4. Field names must match exactly (case-sensitive)
        5. Prohibited field 'timestamp' is not allowed
        """
        # Check that either time or fs is provided (SEP-005 requirement)
        if self.time is None and self.fs is None:
            raise ValueError(
                "Must provide either 'time' or 'fs' to replicate time "
                "information (SEP-005 requirement)"
            )

        # Check time vector length matches data length (SEP-005 requirement)
        if self.time is not None and len(self.time) != len(self.data):
            raise ValueError(
                f"Length of time vector ({len(self.time)}) must match "
                f"data vector length ({len(self.data)}) (SEP-005 requirement)"
            )

        # Validate all timestamp fields are ISO 8601 (SEP-005 requirement)
        for field_name in ["start_timestamp", "end_timestamp"]:
            timestamp = getattr(self, field_name, None)
            if timestamp is not None:
                try:
                    datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                except ValueError as e:
                    raise ValueError(
                        f"{field_name} '{timestamp}' is not valid ISO 8601 "
                        f"format (SEP-005 requirement)"
                    ) from e

        # Field names must match exactly (case-sensitive)
        # Prohibited field 'timestamp' is not allowed
        extra_keys = list((self.__pydantic_extra__ or {}).keys())
        field_names = list(type(self).model_fields.keys())
        for key in extra_keys:
            if key.lower() in [p_key.lower() for p_key in PROHIBITED_FIELDS]:
                raise ValueError(
                    f"'{key}' is a Prohibited keyword, do not use it."
                )
            for field_name in field_names:
                if key.lower() == field_name.lower() and key != field_name:
                    raise ValueError(
                        f"'{key}' is an invalid keyword, "
                        f"please use '{field_name}' instead."
                    )

        return self

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "data": [1.5, 2.3, 1.8, 2.1, 1.9, 2.0, 1.7, 2.2],
                "name": "Wind turbine tower acceleration",
                "unit_str": "m/s²",
                "fs": 100.0,
                "quantity": "a",
                "unit_tex": "m/s$^2$",
                "start_timestamp": "2025-08-16T01:00:00",
                "end_timestamp": "2025-08-16T01:00:08",
            }
        },
    )
