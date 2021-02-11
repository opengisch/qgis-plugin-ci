# Development

## Environment setup

Typically on Ubuntu:

```bash
# create virtual environment linking to system packages (for pyqgis)
python3.8 -m venv .venv

# bump dependencies inside venv
python -m pip install -U pip setuptools wheel
python -m pip install -U -r requirements.txt

# install project as editable
python -m pip install -e .
```
