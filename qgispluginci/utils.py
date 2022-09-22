import logging
import os
import re
from math import floor
from math import log as math_log
from math import pow
from typing import Union

from qgispluginci.version_note import VersionNote

# GLOBALS
logger = logging.getLogger(__name__)


def replace_in_file(file_path: str, pattern, new: str, encoding: str = "utf8"):
    with open(file_path, "r", encoding=encoding) as f:
        content = f.read()
    content = re.sub(pattern, new, content, flags=re.M)
    with open(file_path, "w", encoding=encoding) as f:
        f.write(content)


def configure_file(source_file: str, dest_file: str, replace: dict):
    with open(source_file, "r", encoding="utf-8") as f:
        content = f.read()
    for pattern, new in replace.items():
        content = re.sub(pattern, new, content, flags=re.M)
    with open(dest_file, "w", encoding="utf-8") as f:
        f.write(content)


def convert_octets(octets: int) -> str:
    """Convert a mount of octets in readable size.

    :param int octets: mount of octets to convert

    :Example:

    .. code-block:: python

        >>> convert_octets(1024)
        "1ko"
    """
    # check zero
    if octets == 0:
        return "0 octet"

    # conversion
    size_name = ("octets", "Ko", "Mo", "Go", "To", "Po")
    i = int(floor(math_log(octets, 1024)))
    p = pow(1024, i)
    s = round(octets / p, 2)

    return "%s %s" % (s, size_name[i])


def touch_file(path, update_time: bool = False, create_dir: bool = True):
    basedir = os.path.dirname(path)
    if create_dir and not os.path.exists(basedir):
        os.makedirs(basedir)
    with open(path, "a"):
        if update_time:
            os.utime(path, None)
        else:
            pass


def parse_tag(version_tag: str) -> Union[VersionNote, None]:
    """Parse a tag and determine the semantic version."""
    components = version_tag.split("-")
    items = components[0].split(".")

    try:
        if len(components) == 2:
            return VersionNote(
                major=items[0], minor=items[1], patch=items[2], prerelease=components[1]
            )
        else:
            return VersionNote(major=items[0], minor=items[1], patch=items[2])
    except IndexError:
        return VersionNote()
