#! python3  # noqa: E265

"""
    Metadata about the package to easily retrieve informations about it.

    See: https://packaging.python.org/guides/single-sourcing-package-version/
"""

# ############################################################################
# ########## Libraries #############
# ##################################

# standard library
import os
from datetime import date

# ############################################################################
# ########## Globals #############
# ################################
__all__ = [
    "__author__",
    "__copyright__",
    "__email__",
    "__license__",
    "__summary__",
    "__title__",
    "__title_clean__",
    "__uri__",
    "__version__",
    "__version_info__",
]

__author__ = "Denis Rouzaud, Étienne Trimaille, Julien Moura"
__copyright__ = "2019 - {0}, {1}".format(date.today().year, __author__)
__email__ = "denis.rouzaud@gmail.com"
__license__ = "GNU General Public License v3.0"
__summary__ = (
    "Let qgis-plugin-ci package and release your QGIS plugins for you. "
    "Have a tea or go hiking meanwhile."
    "Contains scripts to perform automated testing and deployment for QGIS plugins. "
    "These scripts are written for and tested on GitHub, Travis-CI, GitHub workflows and Transifex."
)
__title__ = "QGIS Plugin CI"
__title_clean__ = "".join(e for e in __title__ if e.isalnum())
__uri__ = "https://github.com/opengisch/qgis-plugin-ci/"

if os.getenv("CI") == "true":
    # Version is set by the CI with a tag
    __version__ = "__VERSION__"
else:
    # When using pip install -e /local/path/to/this/repo
    __version__ = "0.0.0"

__version_info__ = tuple(
    [
        int(num) if num.isdigit() else num
        for num in __version__.replace("-", ".", 1).split(".")
    ]
)
