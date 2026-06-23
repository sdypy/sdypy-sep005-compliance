SDyPy SEP005 Compliance
-----------------------

This package servers to asses the compability with the SDyPy proposal
for a unified timeseries model.

Installation
------------
Available from pip: 

.. code-block:: python

    pip install sdypy-sep005

Using the package
------------------

Validation is provided by the ``Sep005Data`` Pydantic model, which checks
compliance with the current guidelines.


It's main use case is for the unittests of a custom import wrapper

.. code-block:: python

    from sdypy_sep005 import Sep005Data

    signals = read_from_path(FILE_PATH)  # Your import wrapper
    for channel in signals:
        Sep005Data.model_validate(channel)
