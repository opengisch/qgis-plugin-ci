# Development

## Environment setup

Typically on Ubuntu:

```bash
# create virtual environment linking to system packages (for pyqgis)
python3 -m venv .venv

# install project as editable with dev dependencies
python -m pip install -U -e .[dev  ]

# install git hooks
pre-commit install
```
