#! /usr/bin/env python

# standard
import filecmp
import os
import re
import unittest
import urllib.request
from pathlib import Path
from tempfile import mkstemp
from zipfile import ZipFile

# 3rd party
import yaml
from github import Github, GithubException

# Project
from qgispluginci.changelog import ChangelogParser
from qgispluginci.exceptions import GithubReleaseNotFound
from qgispluginci.parameters import DASH_WARNING, Parameters
from qgispluginci.release import release
from qgispluginci.translation import Translation
from qgispluginci.utils import replace_in_file

# Tests
from .utils import can_skip_test

# If changed, also update CHANGELOG.md
RELEASE_VERSION_TEST = "0.1.2"


class TestRelease(unittest.TestCase):
    def setUp(self):
        with open(".qgis-plugin-ci", "r", encoding="utf8") as f:
            arg_dict = yaml.safe_load(f)
        self.parameters = Parameters(arg_dict)
        self.tx_api_token = os.getenv("tx_api_token")
        self.github_token = os.getenv("github_token")
        self.repo = None
        self.t = None
        if self.github_token:
            print("init Github")
            self.repo = Github(self.github_token).get_repo("opengisch/qgis-plugin-ci")
        self.clean_assets()

    def tearDown(self):
        self.clean_assets()

    def clean_assets(self):
        if self.repo:
            rel = None
            try:
                rel = self.repo.get_release(id=RELEASE_VERSION_TEST)
            except GithubException:
                raise GithubReleaseNotFound(f"Release {RELEASE_VERSION_TEST} not found")
            if rel:
                print("deleting release assets")
                for asset in rel.get_assets():
                    print(f"  delete {asset.name}")
                    asset.delete_asset()
        if self.t:
            self.t._t.delete_project(self.parameters.project_slug)

    def test_release(self):
        release(self.parameters, RELEASE_VERSION_TEST)

    @unittest.skipIf(can_skip_test(), "Missing tx_api_token")
    def test_release_with_transifex(self):
        Translation(self.parameters, tx_api_token=self.tx_api_token)
        release(self.parameters, RELEASE_VERSION_TEST, tx_api_token=self.tx_api_token)

    def test_zipname(self):
        """Tests about the zipname for the QGIS plugin manager.

        See #22 about dash
        and also capital letters
        """
        self.assertEqual(
            "my_plugin-experimental.0.0.0.zip",
            Parameters.archive_name("my_plugin", "0.0.0", True),
        )

        self.assertEqual(
            "My_Plugin.0.0.0.zip", Parameters.archive_name("My_Plugin", "0.0.0", False)
        )

        with self.assertLogs(
            logger="qgispluginci.parameters", level="WARNING"
        ) as captured:
            Parameters.archive_name("my-plugin", "0.0.0")
        self.assertEqual(
            len(captured.records), 1
        )  # check that there is only one log message
        self.assertEqual(captured.records[0].getMessage(), DASH_WARNING)

    @unittest.skipIf(can_skip_test(), "Missing github_token")
    def test_release_upload_github(self):
        release(
            self.parameters,
            RELEASE_VERSION_TEST,
            github_token=self.github_token,
            upload_plugin_repo_github=True,
        )

        # check the custom plugin repo
        _, xml_repo = mkstemp(suffix=".xml")
        url = f"https://github.com/opengisch/qgis-plugin-ci/releases/download/{RELEASE_VERSION_TEST}/plugins.xml"
        print(f"retrieve repo from {url}")
        urllib.request.urlretrieve(url, xml_repo)
        replace_in_file(
            xml_repo,
            r"<update_date>[\w-]+<\/update_date>",
            "<update_date>__TODAY__</update_date>",
        )
        if not filecmp.cmp("test/plugins.xml.expected", xml_repo, shallow=False):
            import difflib

            with open("test/plugins.xml.expected") as f:
                text1 = f.readlines()
            with open(xml_repo) as f:
                text2 = f.readlines()
            self.assertFalse(True, "\n".join(difflib.unified_diff(text1, text2)))

        # compare archive file size
        gh_release = self.repo.get_release(id=RELEASE_VERSION_TEST)
        archive_name = self.parameters.archive_name(
            self.parameters.plugin_path, RELEASE_VERSION_TEST
        )
        fs = os.path.getsize(archive_name)
        print("size: ", fs)
        self.assertGreater(fs, 0, "archive file size must be > 0")
        found = False
        for a in gh_release.get_assets():
            if a.name == archive_name:
                found = True
                self.assertEqual(fs, a.size, "asset size doesn't march archive size.")
                break
        self.assertTrue(found, "asset not found")

    def test_release_changelog(self):
        """Test if changelog in metadata.txt inside zipped plugin after release command."""
        # variables
        cli_config_changelog = Path("test/fixtures/.qgis-plugin-ci-test-changelog.yaml")
        version_to_release = "0.1.2"

        # load specific parameters
        with cli_config_changelog.open() as in_cfg:
            arg_dict = yaml.safe_load(in_cfg)
        parameters = Parameters(arg_dict)
        self.assertIsInstance(parameters, Parameters)

        # get output zip path
        archive_name = parameters.archive_name(
            plugin_name=parameters.plugin_path, release_version=version_to_release
        )

        # extract last items from changelog
        parser = ChangelogParser()
        self.assertTrue(parser.has_changelog())
        changelog_lastitems = parser.last_items(
            count=parameters.changelog_number_of_entries
        )

        # Include a changelog
        release(
            parameters=parameters,
            release_version=version_to_release,
            allow_uncommitted_changes=True,
        )

        # open archive and compare
        with ZipFile(archive_name, "r") as zip_file:
            data = zip_file.read(f"{parameters.plugin_path}/metadata.txt")

        # Changelog
        self.assertGreater(
            data.find(bytes(changelog_lastitems, "utf8")),
            0,
            f"changelog detection failed in release: {data}",
        )

        # Commit number
        self.assertEqual(1, len(re.findall(r"commitNumber=\d+", str(data))))

        # Commit sha1 not in the metadata.txt
        self.assertEqual(0, len(re.findall(r"commitSha1=\d+", str(data))))


if __name__ == "__main__":
    unittest.main()
