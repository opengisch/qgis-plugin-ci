import logging
import os
import subprocess
from pathlib import Path

from qgispluginci.changelog import ChangelogParser

default_version = "0.dev"

__version__ = os.getenv("QGISPLUGINCI_VERSION", default_version)

if __version__ == default_version:
    # try to get it from git tag
    try:
        git_cmd = "git tag -l --sort=-creatordate | head -n 1"
        returned_output: bytes = subprocess.check_output(git_cmd, shell=True)
        __version__ = returned_output.decode("utf-8")
    except Exception as err:
        logging.debug(f"Unable to retrieve version from latest git tag. Trace: {err}")

    if not len(__version__):
        chglog = ChangelogParser(parent_folder=Path(__file__).parent.parent)
        if chglog.CHANGELOG_FILEPATH:
            __version__ = chglog.latest_version()

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
