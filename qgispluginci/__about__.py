#! python3  # noqa: E265

"""
    Metadata about the package to easily retrieve informations about it.

    See: https://packaging.python.org/guides/single-sourcing-package-version/
"""

# ############################################################################
# ########## Libraries #############
# ##################################

# standard library
from datetime import date

# ############################################################################
# ########## Globals #############
# ################################
__all__ = [
    "__authors__",
    "__copyright__",
    "__license__",
    "__summary__",
    "__title__",
    "__title_clean__",
    "__uri__",
    "__version__",
    "__version_info__",
]

authors_data = [
    {"name": "Denis Rouzaud", "email": "denis@opengis.ch"},
    {"name": "Etienne Trimaille", "email": "etienne.trimaille@gmail.com"},
    {"name": "Julien Moura", "email": "julien.moura@gmail.com"},
]

__authors__ = ", ".join([a["name"] for a in authors_data])
__copyright__ = f"2019 - {date.today().year}, {__authors__}"
__license__ = "GNU General Public License v3.0"
__title__ = "QGIS Plugin CI"
__title_clean__ = "".join(e for e in __title__ if e.isalnum())
__uri__ = ""
__uri_homepage__ = ""
__uri_tracker__ = f"{__uri__}issues/"
with open("DESCRIPTION", "r") as f:
    __summary__ = f.readlines()

# This string might be updated on CI on runtime with a proper semantic version name with X.Y.Z
__version__ = "__VERSION__"

if "." not in __version__:
    # If __version__ is still not a proper semantic versioning with X.Y.Z
    # let's hardcode 0.0.0
    __version__ = "0.dev"

__version_info__ = tuple(
    [
        int(num) if num.isdigit() else num
        for num in __version__.replace("-", ".", 1).split(".")
    ]
)
