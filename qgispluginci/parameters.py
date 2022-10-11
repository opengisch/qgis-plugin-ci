#! python3  # noqa E265

"""
    Parameters management.
"""

# ############################################################################
# ########## Libraries #############
# ##################################

# standard library
import datetime
import logging
import os
import re
import sys

# 3rd party
from slugify import slugify

# ############################################################################
# ########## Globals #############
# ################################


DASH_WARNING = "Dash in the plugin name is causing issues with QGIS plugin manager"

logger = logging.getLogger(__name__)


# ############################################################################
# ########## Classes #############
# ################################


class Parameters:
    """
    Attributes
    ----------
    plugin_path: str
        The directory of the source code in the repository.
        Defaults to: `slugify(plugin_name)`

    github_organization_slug: str
        The organization slug on SCM host (e.g. Github) and translation platform (e.g. Transifex).
        Not required when running on Travis since deduced from `$TRAVIS_REPO_SLUG`environment variable.

    project_slug: str
        The project slug on SCM host (e.g. Github) and translation platform (e.g. Transifex).
        Not required when running on Travis since deduced from `$TRAVIS_REPO_SLUG`environment variable.

    transifex_coordinator: str
        The username of the coordinator in Transifex.
        Required to create new languages.

    transifex_organization: str
        The organization name in Transifex
        Defaults to: the GitHub organization slug

    transifex_project: str
        The project on Transifex, which can be different from the one on GitHub.
        Defaults to: the project_slug

    transifex_resource: str
        The resource name in transifex
        Defaults to: the project_slug

    translation_source_language:
        The source language for translations.
        Defaults to: 'en'

    translation_languages:
        List of languages.

    changelog_include:
        If the changelog must be added when releasing a version AND if there is a CHANGELOG.md file
        Defaults to True

    changelog_path:
        Path to the CHANGELOG.md relative to the configuration file. Defaults to CHANGELOG.md

    changelog_number_of_entries:
        Number of changelog entries to add in the metdata.txt
        Defaults to 3

    create_date: datetime.date
        The date of creation of the plugin.
        The would be used in the custom repository XML.
        Format: YYYY-MM-DD

    lrelease_path: str
        The path of lrelease executable

    pylupdate5_path: str
        The path of pylupdate executable


    """

    def __init__(self, definition: dict):
        self.plugin_path = definition.get("plugin_path")
        self.plugin_name = self.__get_from_metadata("name")
        self.plugin_slug = slugify(self.plugin_name)
        self.project_slug = definition.get(
            "project_slug",
            os.environ.get("TRAVIS_REPO_SLUG", f".../{self.plugin_slug}").split("/")[1],
        )
        self.github_organization_slug = definition.get(
            "github_organization_slug",
            os.environ.get("TRAVIS_REPO_SLUG", "").split("/")[0],
        )
        self.transifex_coordinator = definition.get("transifex_coordinator", "")
        self.transifex_organization = definition.get(
            "transifex_organization", self.github_organization_slug
        )
        self.translation_source_language = definition.get(
            "translation_source_language", "en"
        )
        self.translation_languages = definition.get("translation_languages", {})
        self.transifex_project = definition.get("transifex_project", self.project_slug)
        self.transifex_resource = definition.get(
            "transifex_resource", self.project_slug
        )
        self.create_date = datetime.datetime.strptime(
            str(definition.get("create_date", datetime.date.today())), "%Y-%m-%d"
        )
        self.lrelease_path = definition.get("lrelease_path", "lrelease")
        self.pylupdate5_path = definition.get("pylupdate5_path", "pylupdate5")
        changelog_include = definition.get("changelog_include", True)
        if isinstance(changelog_include, str):
            self.changelog_include = changelog_include.lower() in [
                "true",
                "1",
                "t",
                "y",
            ]
        else:
            self.changelog_include = changelog_include
        self.changelog_number_of_entries = definition.get(
            "changelog_number_of_entries", 3
        )
        self.changelog_path = definition.get("changelog_path", "CHANGELOG.md")

        # read from metadata
        if not self.plugin_path:
            # This tool can be used outside of a QGIS plugin to read a changelog file
            return

        self.author = self.__get_from_metadata("author", "")
        self.description = self.__get_from_metadata("description")
        self.qgis_minimum_version = self.__get_from_metadata("qgisMinimumVersion")
        self.icon = self.__get_from_metadata("icon", "")
        self.tags = self.__get_from_metadata("tags", "")
        self.experimental = self.__get_from_metadata("experimental", False)
        self.deprecated = self.__get_from_metadata("deprecated", False)
        self.issue_tracker = self.__get_from_metadata("tracker")
        self.homepage = self.__get_from_metadata("homepage", "")
        if self.homepage == "":
            logger.warning(
                "Homepage is not given in the metadata. "
                "It is a mandatory information to publish "
                "the plugin on the QGIS official repository."
            )
        self.repository_url = self.__get_from_metadata("repository")

    @staticmethod
    def archive_name(
        plugin_name, release_version: str, experimental: bool = False
    ) -> str:
        """
        Returns the archive file name
        """
        # zipname: use dot before version number
        # and not dash since it's causing issues #22
        if "-" in plugin_name:
            logger.warning(DASH_WARNING)

        experimental = "-experimental" if experimental else ""
        return f"{plugin_name}{experimental}.{release_version}.zip"

    def __get_from_metadata(self, key: str, default_value: any = None) -> str:
        if not self.plugin_path:
            return ""

        metadata_file = f"{self.plugin_path}/metadata.txt"
        with open(metadata_file) as f:
            for line in f:
                m = re.match(rf"{key}\s*=\s*(.*)$", line)
                if m:
                    return m.group(1)
        if default_value is None:
            logger.error(f"Mandatory key is missing in metadata: {key}")
            sys.exit(1)
        return default_value


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    pass
