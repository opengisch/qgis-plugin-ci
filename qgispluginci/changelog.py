#! python3  # noqa E265

"""
    Changelog parser. Following <https://keepachangelog.com/en/1.0.0/>.
"""

# ############################################################################
# ########## Libraries #############
# ##################################

# standard library
import logging
import re
import sys
from pathlib import Path
from typing import Union

from qgispluginci.version_note import VersionNote

# ############################################################################
# ########## Globals #############
# ################################

# see: https://regex101.com/r/8JROUv/1
CHANGELOG_REGEXP = r"(?<=##)\s*\[*(v?0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)\]?(\(.*\))?(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?\]*\s-\s*([\d\-/]{10})(.*?)(?=##|\Z)"
logger = logging.getLogger(__name__)

# ############################################################################
# ########## Classes #############
# ################################


class ChangelogParser:
    CHANGELOG_FILEPATH: Union[Path, None] = None

    @classmethod
    def has_changelog(
        cls, parent_folder: Union[Path, str] = Path("."), changelog_path="CHANGELOG.md"
    ) -> bool:
        """Check if a changelog file exists within the parent folder. If it does, \
        it returns True and the file path is stored as class attribute. If not, it \
        returns False and the class attribute is reset to None.

        Args:
            parent_folder (Union[Path, str], optional): parent folder where to look \
                for a `CHANGELOG.md` file. Defaults to Path(".").

            changelog_path str: Path relative to parent_folder. Defaults to CHANGELOG.md.

        Raises:
            FileExistsError: if the parent_folder path doesn't exist
            TypeError: if the path is not a folder but a path

        Returns:
            bool: True if a CHANGELOG.md exists within the parent_folder
        """
        # reset stored path as class attribute
        cls.CHANGELOG_FILEPATH = None

        # ensure using pathlib.Path
        if isinstance(parent_folder, str):
            parent_folder = Path(parent_folder)

        # check if the folder exists
        if not parent_folder.exists():
            logger.error(
                f"Parent folder doesn't exist: {parent_folder.resolve()}",
                exc_info=FileExistsError(),
            )
            sys.exit(1)
        # check if path is a folder
        if not parent_folder.is_dir():
            logger.error(
                f"Path is not a folder: {parent_folder.resolve()}", exc_info=TypeError()
            )
            sys.exit(1)

        # build, check and store the changelog path
        cls.CHANGELOG_FILEPATH = parent_folder / changelog_path
        if cls.CHANGELOG_FILEPATH.is_file():
            logger.info(f"Changelog file used: {cls.CHANGELOG_FILEPATH.resolve()}")
            return True
        else:
            logger.warning(
                f"Changelog file doesn't exist: {cls.CHANGELOG_FILEPATH.resolve()}"
            )
            cls.CHANGELOG_FILEPATH = None
            return False

    def __init__(
        self,
        parent_folder: Union[Path, str] = Path("."),
        changelog_path: str = "CHANGELOG.md",
    ):
        self.has_changelog(parent_folder=parent_folder, changelog_path=changelog_path)

    def _parse(self):
        if not self.CHANGELOG_FILEPATH:
            return None

        with self.CHANGELOG_FILEPATH.open(mode="r", encoding="UTF8") as f:
            content = f.read()

        return re.findall(
            pattern=CHANGELOG_REGEXP, string=content, flags=re.MULTILINE | re.DOTALL
        )

    def last_items(self, count: int) -> str:
        """Content to add in the metadata.txt.

        Args:
            count (int): Maximum number of tags to include in the file.

        Returns:
            str: changelog extraction ready to be added to metadata.txt
        """
        changelog_content = self._parse()
        if not changelog_content:
            return ""

        count = int(count)
        output = "\n"

        for version in changelog_content[0:count]:
            version_note = VersionNote(*version)
            output += f" Version {version_note.version}:\n"
            for item in version_note.text.split("\n"):
                if item:
                    output += f" {item}\n"
            output += "\n"
        return output

    def _version_note(self, tag: str) -> Union[VersionNote, None]:
        """Get the tuple for a given version."""
        changelog_content = self._parse()
        if not len(changelog_content):
            logger.error(
                f"Parsing the changelog ({self.CHANGELOG_FILEPATH.resolve()}) "
                "returned an empty content."
            )
            return None

        if tag == "latest":
            return VersionNote(*changelog_content[0])

        for version in changelog_content:
            version_note = VersionNote(*version)
            if version_note.version == tag:
                return version_note

    def latest_version(self) -> str:
        """Return the latest tag described in the changelog file."""
        latest = self._version_note("latest")
        logger.debug(
            "Latest version retrieved from changelog "
            f"({self.CHANGELOG_FILEPATH.resolve()}): {latest.version}"
        )
        return latest.version

    def content(self, tag: str) -> Union[str, None]:
        """Get a version content to add in a release according to the version name."""
        version_note = self._version_note(tag)
        if not version_note:
            return None

        return version_note.text


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    pass
