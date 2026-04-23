#! python3

# standard library
import logging
import os
import re
from datetime import date, datetime, timezone
from math import floor, log as math_log, pow as math_pow
from zoneinfo import ZoneInfo

# package
from qgispluginci.version_note import VersionNote


# GLOBALS
logger = logging.getLogger(__name__)


def replace_in_file(file_path: str, pattern: str, new: str, encoding: str = "utf8"):
    with open(file_path, encoding=encoding) as f:
        content = f.read()
    content = re.sub(pattern, new, content, flags=re.M)
    with open(file_path, "w", encoding=encoding) as f:
        f.write(content)


def configure_file(source_file: str, dest_file: str, replace: dict):
    with open(source_file, encoding="utf-8") as f:
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
    p = math_pow(1024, i)
    s = round(octets / p, 2)

    return f"{s} {size_name[i]}"


def touch_file(path: str, update_time: bool = False, create_dir: bool = True):
    basedir = os.path.dirname(path)
    if create_dir and not os.path.exists(basedir):
        os.makedirs(basedir)
    with open(path, "a"):
        if update_time:
            os.utime(path, None)
        else:
            pass


def parse_tag(version_tag: str) -> VersionNote | None:
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


def set_datetime_zoneinfo(
    input_datetime: date | datetime, config_timezone: str = "UTC"
) -> datetime:
    """Apply timezone to a naive datetime or date.

    Args:
        input_datetime (date | datetime): offset-naive datetime
        config_timezone (str, optional): name of timezone as registered in IANA
            database. Defaults to "UTC". Example : Europe/Paris.

    Returns:
        datetime: offset-aware datetime
    """
    if isinstance(input_datetime, date):
        input_datetime = datetime.combine(date=input_datetime, time=datetime.min.time())
        logger.debug(
            f"Input is a date, converted to datetime with time set to 00:00:00: {input_datetime}"
        )

    if input_datetime.tzinfo:
        logger.debug(
            f"Input datetime already has timezone info: {input_datetime.tzinfo}, no conversion applied."
        )
        return input_datetime
    elif not config_timezone:
        logger.debug("No timezone provided in config, applying UTC timezone.")
        return input_datetime.replace(tzinfo=timezone.utc)
    else:
        config_tz = ZoneInfo(config_timezone)
        logger.debug(
            f"Applying timezone from config: {config_timezone} to input datetime."
        )
        return input_datetime.replace(tzinfo=config_tz)
