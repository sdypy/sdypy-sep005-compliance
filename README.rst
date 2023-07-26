SDyPy SEP005 Compliance
-----------------------

This package servers to asses the compability with the SDyPy proposal
for a unified timeseries model.

Using the package
------------------

The main function is the ``assert_sep005`` function that serves to
validate whether a function return is compliant with the current guidelines.


It's main use case is for the unittests of a custom import wrapper

.. code-block:: python

    from sdypy_sep005.sep005 import assert_sep005

    signals = read_from_path(FILE_PATH) # Your import wrapper
    assert_sep005(signals)
