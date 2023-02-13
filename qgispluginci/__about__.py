#! python3  # noqa: E265

"""
    Metadata about the package to easily retrieve informations about it.

    See: https://packaging.python.org/guides/single-sourcing-package-version/
"""

# ############################################################################
# ########## Libraries #############
# ##################################

# standard library
import logging
import subprocess
from datetime import date
from os import getenv
from pathlib import Path

# package
from qgispluginci.changelog import ChangelogParser

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
__copyright__ = f"2019 - {date.today().year}, {__author__}"
__email__ = "denis.rouzaud@gmail.com"
__license__ = "GNU General Public License v3.0"
__summary__ = (
    "Let qgis-plugin-ci package and release your QGIS plugins for you. "
    "Have a tea or go hiking meanwhile.\n"
    "Contains scripts to perform automated testing and deployment for QGIS plugins. "
    "These scripts are written for and tested on GitHub Actions, GitLab CI, "
    "Travis-CI, and Transifex."
)
__title__ = "QGIS Plugin CI"
__title_clean__ = "".join(e for e in __title__ if e.isalnum())
__uri__ = "https://github.com/opengisch/qgis-plugin-ci/"
__uri_homepage__ = "https://opengisch.github.io/qgis-plugin-ci/"
__uri_tracker__ = f"{__uri__}issues/"

# This string might be updated on CI on runtime with a proper semantic version name with X.Y.Z
__version__ = getenv("GITHUB_REF_NAME", "__VERSION__")

if "." not in __version__:
    # If __version__ is still not a proper semantic versioning with X.Y.Z
    # let's hardcode 0.0.0
    __version__ = "0.0.0"

    # try to get it from git tag
    try:
        git_cmd = "git tag -l --sort=-creatordate | head -n 1"
        returned_output: bytes = subprocess.check_output(git_cmd, shell=True)
        if len(returned_output):
            __version__ = returned_output.decode("utf-8")
        else:
            chglog = ChangelogParser(parent_folder=Path(__file__).parent.parent)
            if chglog.CHANGELOG_FILEPATH:
                __version__ = chglog.latest_version()
    except Exception as err:
        logging.debug(f"Unable to retrieve version from latest git tag. Trace: {err}")

    try:
        # bump latest number
        M, m, p = __version__.split(".")
        __version__ = f"{M}.{m}.{int(p)+ 1}.dev"
    except Exception as err:
        logging.debug(f"Unable to parse version to bump latest number. Trace: {err}")
        __version__ = f"{__version__}.dev"

__version_info__ = tuple(
    [
        int(num) if num.isdigit() else num
        for num in __version__.replace("-", ".", 1).split(".")
    ]
)
