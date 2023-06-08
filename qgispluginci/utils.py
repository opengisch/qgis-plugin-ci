import configparser
import logging
import os
import re
from math import floor
from math import log as math_log
from math import pow
from typing import Any, Dict, Optional, Union

import toml
import yaml

from qgispluginci.exceptions import ConfigurationNotFound
from qgispluginci.parameters import Parameters
from qgispluginci.version_note import VersionNote

# GLOBALS
logger = logging.getLogger(__name__)


def replace_in_file(file_path: str, pattern, new: str, encoding: str = "utf8"):
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


def make_parameters(args=None, config_file: Optional[str] = None) -> Parameters:
    """
    Make a Dict from a config file or by exploring the filesystem
    Accepts an argparse Namespace for backward compatibility.
    """
    configuration_not_found = ConfigurationNotFound(
        ".qgis-plugin-ci or setup.cfg or pyproject.toml with a 'qgis-plugin-ci' section have not been found."
    )

    def explore_config() -> Dict[str, Any]:
        if os.path.isfile(".qgis-plugin-ci"):
            # We read the .qgis-plugin-ci file
            with open(".qgis-plugin-ci", encoding="utf8") as f:
                arg_dict = yaml.safe_load(f)
        elif os.path.isfile("pyproject.toml"):
            # We read the pyproject.toml file
            with open("pyproject.toml", encoding="utf8") as f:
                arg_dict = toml.load(f)
        else:
            config = configparser.ConfigParser()
            config.read("setup.cfg")
            if "qgis-plugin-ci" in config.sections():
                # We read the setup.cfg file
                arg_dict = dict(config.items("qgis-plugin-ci"))
            else:
                # We don't have either a .qgis-plugin-ci or a setup.cfg
                if args and args.command == "changelog":
                    # but for the "changelog" sub command, the config file is not required, we can continue
                    arg_dict = dict()
                else:
                    raise configuration_not_found
        return arg_dict

    def load_config(filename: str) -> Dict[str, Any]:
        if filename == "setup.cfg":
            config = configparser.ConfigParser()
            config.read(filename)
            return dict(config.items("qgis-plugin-ci"))

        _, suffix = filename.rsplit(".", 1)

        with open(filename) as f:
            if suffix == "toml":
                return toml.load(f)
            elif suffix in {"yaml", "yml"}:
                return yaml.safe_load(f)

        raise configuration_not_found

    if config_file:
        config_dict = load_config(config_file)
    else:
        config_dict = explore_config()

    return Parameters(config_dict)


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

    return f"{s} {size_name[i]}"


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
