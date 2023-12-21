#! /usr/bin/env python

# standard
import argparse
import filecmp
import os
import re
import unittest
import urllib.request
from itertools import product
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
        self.setup_params = Parameters.make_from(
            path_to_config_file=Path("test/fixtures/setup.cfg")
        )
        self.qgis_plugin_config_params = Parameters.make_from(
            path_to_config_file=Path("test/fixtures/.qgis-plugin-ci")
        )
        self.pyproject_params = Parameters.make_from(
            path_to_config_file=Path("test/fixtures/pyproject.toml")
        )
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
            self.t._t.delete_project(self.qgis_plugin_config_params.project_slug)

    def test_dict_from_config(self):
        with self.subTest():
            self.assertTrue(dict(self.qgis_plugin_config_params))
            self.assertTrue(dict(self.pyproject_params))
            self.assertTrue(dict(self.setup_params))

    def test_release_from_dot_qgis_plugin_ci(self):
        release(self.qgis_plugin_config_params, RELEASE_VERSION_TEST)

    def test_release_from_pyproject(self):
        print(self.pyproject_params)
        release(self.pyproject_params, RELEASE_VERSION_TEST)

    @unittest.skipIf(can_skip_test(), "Missing tx_api_token")
    def test_release_with_transifex(self):
        Translation(self.qgis_plugin_config_params, tx_api_token=self.tx_api_token)
        release(
            self.qgis_plugin_config_params,
            RELEASE_VERSION_TEST,
            tx_api_token=self.tx_api_token,
        )

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
            self.qgis_plugin_config_params,
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
        archive_name = self.qgis_plugin_config_params.archive_name(
            self.qgis_plugin_config_params.plugin_path, RELEASE_VERSION_TEST
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

    def test_release_version_valid_invalid(self):
        valid_tags = ["v1.1.1", "v1.1", "1.0.1", "1.1", "1.0.0-alpha", "1.0.0-dev"]
        invalid_tags = ["1", "v1", ".", ".1"]
        expected_valid_results = {
            "v1.1.1": ["v3"],
            "v1.1": ["v2"],
            "1.0.1": ["double", "semver"],
            "1.1": ["simple"],
            "1.0.0-alpha": ["semver"],
            "1.0.0-dev": ["semver"],
        }
        valid_results = {tag: [] for tag in valid_tags}
        patterns = Parameters.get_release_version_patterns()
        for key, cand in product(patterns, valid_results):
            if re.match(patterns[key], cand):
                valid_results[cand].append(key)
        self.assertEqual(valid_results, expected_valid_results)

        invalid_results = {tag: [] for tag in invalid_tags}
        for key, cand in product(patterns, invalid_results):
            if re.match(patterns[key], cand):
                invalid_results[cand].append(key)
        self.assertFalse(any(invalid_results.values()))

    def test_release_version_validation_on(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(
            title="commands", description="qgis-plugin-ci command", dest="command"
        )
        sub_parser = subparsers.add_parser("package")
        sub_parser.add_argument("release_version")
        sub_parser.add_argument("--no-validation", action="store_true")
        args = parser.parse_args(["package", "v1"])
        with self.assertRaises(ValueError):
            Parameters.validate_args(args)

    def test_release_version_validation_off(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(
            title="commands", description="qgis-plugin-ci command", dest="command"
        )
        sub_parser = subparsers.add_parser("package")
        sub_parser.add_argument("release_version")
        sub_parser.add_argument("--no-validation", action="store_true")
        args = parser.parse_args(["package", "v1", "--no-validation"])
        Parameters.validate_args(args)


if __name__ == "__main__":
    unittest.main()
