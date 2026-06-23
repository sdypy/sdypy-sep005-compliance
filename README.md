# SDyPy SEP005 Compliance

This package serves to assess the compatibility with the SDyPy proposal for a
unified timeseries model.

## Installation

Available from PyPI:

```bash
pip install sdypy-sep005
```

## Using the package

Validation is provided by the `Sep005Data` Pydantic model, which checks
compliance with the current guidelines.

Its main use case is for the unit tests of a custom import wrapper:

```python
from sdypy_sep005 import Sep005Data

signals = read_from_path(FILE_PATH)  # Your import wrapper
for channel in signals:
    Sep005Data.model_validate(channel)
```

## Contributing

Contributions are welcome and greatly appreciated!

### Workflow

A bug fix or enhancement is delivered using a pull request. A good pull request
should cover one bug fix or enhancement feature. This keeps the change set easier
to review and less likely to need major rework or rejection.

The workflow that developers typically use is as follows.

1. Fork the [sdypy-sep005-compliance](https://github.com/OWI-Lab/sdypy-sep005-compliance)
   repository into your account.

2. Clone the source onto your development machine:

   ```bash
   git clone https://github.com/OWI-Lab/sdypy-sep005-compliance.git
   cd sdypy-sep005-compliance
   ```

3. Install [uv](https://docs.astral.sh/uv/) and sync the project dependencies:

   ```bash
   uv sync
   ```

   This creates a virtual environment and installs the default dependency groups
   (`ci` and `test`) defined in `pyproject.toml`.

4. Create a branch for local development:

   ```bash
   git checkout -b name-of-your-bugfix-or-feature
   ```

5. Develop your fix or enhancement:

   - Make a fix or enhancement (for example, modify a class, method, function,
     or module).
   - Update an existing unit test or create a new unit test module to verify
     the change works as expected.
   - Run the test suite:

     ```bash
     uv run pytest
     ```

6. Update the docs for anything but trivial bug fixes, then build them to verify
   the result:

   ```bash
   uv sync --group docs
   cd docs
   uv run make clean
   uv run make html
   ```

7. Commit and push changes to your fork:

   ```bash
   git add .
   git commit -m "A detailed description of the changes."
   git push origin name-of-your-bugfix-or-feature
   ```

   A pull request should preferably only have one commit upon the current
   `main` HEAD (via rebases and squash).

8. Submit a pull request through GitHub.

9. Check that automated continuous integration steps all pass. Fix any problems
   if necessary and update the pull request.
