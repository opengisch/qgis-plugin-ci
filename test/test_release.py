#! /usr/bin/env python

# standard
import argparse
import difflib
import filecmp
import os
import re
import unittest
import unittest.mock
import urllib.request
from itertools import product
from pathlib import Path
from tempfile import TemporaryDirectory, mkstemp
from zipfile import ZipFile

# 3rd party
import yaml
from github import Github, GithubException

# Project
from qgispluginci import __version__
from qgispluginci.changelog import ChangelogParser
from qgispluginci.exceptions import GithubReleaseNotFound
from qgispluginci.parameters import DASH_WARNING, Parameters
from qgispluginci.release import (
    create_plugin_repo,
    release,
    upload_plugin_to_osgeo_with_token,
)
from qgispluginci.translation import Translation
from qgispluginci.utils import replace_in_file

# Tests
from test.utils import can_skip_test_github, can_skip_test_transifex


# If changed, also update CHANGELOG.md
RELEASE_VERSION_TEST = "0.1.2"
STYLESHEET_DECLARATION_LINE = '<?xml-stylesheet type="text/xsl" href="plugins.xsl"?>'


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
            self.repo = Github(self.github_token).get_repo("qgis/qgis-plugin-ci")
        self.clean_assets()

    def tearDown(self):
        self.clean_assets()

    def clean_assets(self):
        if self.repo:
            rel = None
            try:
                rel = self.repo.get_release(id=RELEASE_VERSION_TEST)
            except GithubException:
                raise GithubReleaseNotFound(f"Release {RELEASE_VERSION_TEST} not found")  # noqa: B904
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

    def test_release_with_empty_tx_token(self):
        release(
            self.qgis_plugin_config_params,
            RELEASE_VERSION_TEST,
            tx_api_token="",
        )

    @unittest.skipIf(
        can_skip_test_github() or can_skip_test_transifex(),
        "Missing github_token or tx_api_token",
    )
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
            "my_plugin.0.0.0.zip",
            Parameters.archive_name("my_plugin", "0.0.0"),
        )

        with self.assertLogs(
            logger="qgispluginci.parameters", level="WARNING"
        ) as captured:
            Parameters.archive_name("my-plugin", "0.0.0")
        self.assertEqual(
            len(captured.records), 1
        )  # check that there is only one log message
        self.assertEqual(captured.records[0].getMessage(), DASH_WARNING)

    @unittest.skipIf(can_skip_test_github(), "Missing github_token")
    def test_release_upload_github(self):
        release(
            self.qgis_plugin_config_params,
            RELEASE_VERSION_TEST,
            github_token=self.github_token,
            upload_plugin_repo_github=True,
        )

        # check the custom plugin repo
        _, xml_repo = mkstemp(suffix=".xml")
        url = f"https://github.com/qgis/qgis-plugin-ci/releases/download/{RELEASE_VERSION_TEST}/plugins.xml"
        print(f"retrieve repo from {url}")
        urllib.request.urlretrieve(url, xml_repo)
        replace_in_file(
            xml_repo,
            r"<update_date>[^<]+<\/update_date>",
            "<update_date>__TODAY__</update_date>",
        )

        replace_in_file(
            xml_repo,
            r'generator_version="[^"]+"',
            'generator_version="__GENERATOR_VERSION__"',
        )

        if not filecmp.cmp("test/plugins.xml.expected", xml_repo, shallow=False):
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
            license_data = zip_file.read(f"{parameters.plugin_path}/LICENSE")

        # Changelog
        self.assertGreater(
            data.find(bytes(changelog_lastitems, "utf8")),
            0,
            f"changelog detection failed in release: {data}",
        )

        # License
        self.assertGreater(
            license_data.find(bytes("GNU GENERAL PUBLIC LICENSE", "utf8")),
            0,
            "license file content mismatch",
        )

        # Commit number
        self.assertEqual(1, len(re.findall(r"commitNumber=\d+", str(data))))

        # Commit sha1 not in the metadata.txt
        self.assertEqual(0, len(re.findall(r"commitSha1=\d+", str(data))))

    def test_release_version_valid_invalid(self):
        valid_tags = [
            "v1.1.1",
            "v1.1",
            "1.0.1",
            "1.1",
            "1.0.0-alpha",
            "1.0.0-dev",
            "latest",
        ]
        invalid_tags = ["1", "v1", ".", ".1"]
        expected_valid_results = {
            "v1.1.1": ["v3"],
            "v1.1": ["v2"],
            "1.0.1": ["double", "semver"],
            "1.1": ["simple"],
            "1.0.0-alpha": ["semver"],
            "1.0.0-dev": ["semver"],
            "latest": ["latest"],
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

    def test_create_plugin_repo_with_stylesheet(self):
        """Stylesheet line must be present in the XML and the XSL file must be copied alongside."""
        archive_name = self.qgis_plugin_config_params.archive_name(
            self.qgis_plugin_config_params.plugin_path, RELEASE_VERSION_TEST
        )
        original_dir = Path().cwd()
        with TemporaryDirectory() as tmp_dir:
            try:
                os.chdir(tmp_dir)
                returned_path = create_plugin_repo(
                    parameters=self.qgis_plugin_config_params,
                    release_version=RELEASE_VERSION_TEST,
                    release_tag=RELEASE_VERSION_TEST,
                    archive=archive_name,
                    osgeo_username="",
                    plugin_repo_url="https://oslandia.gitlab.io/qgis/oslandia/",
                    plugin_repo_stylesheet=True,
                )
                content = Path(returned_path).read_text(encoding="utf-8")
                self.assertIn(
                    STYLESHEET_DECLARATION_LINE,
                    content,
                    "Stylesheet process instruction line must be present in XML",
                )

                xsl_sibling = Path(returned_path).parent / "plugins.xsl"
                self.assertTrue(
                    xsl_sibling.is_file(),
                    f"plugins.xsl must be copied alongside plugins.xml (looked in {xsl_sibling})",
                )
            finally:
                os.chdir(original_dir)

    def test_create_plugin_repo_disable_stylesheet(self):
        """No stylesheet line in the XML and no XSL file copied when disable_stylesheet=True."""
        archive_name = self.qgis_plugin_config_params.archive_name(
            self.qgis_plugin_config_params.plugin_path, RELEASE_VERSION_TEST
        )
        original_dir = Path().cwd()
        with TemporaryDirectory() as tmp_dir:
            try:
                os.chdir(tmp_dir)
                returned_path = create_plugin_repo(
                    parameters=self.qgis_plugin_config_params,
                    release_version=RELEASE_VERSION_TEST,
                    release_tag=RELEASE_VERSION_TEST,
                    archive=archive_name,
                    osgeo_username="",
                    plugin_repo_url="https://example.com/",
                    plugin_repo_stylesheet=False,
                )
                content = Path(returned_path).read_text(encoding="utf-8")
                self.assertNotIn(
                    STYLESHEET_DECLARATION_LINE,
                    content,
                    "Stylesheet process instruction line must be absent when disable_stylesheet=True",
                )

                xsl_sibling = Path(returned_path).parent / "plugins.xsl"
                self.assertFalse(
                    xsl_sibling.is_file(),
                    "plugins.xsl must not be copied when disable_stylesheet=True",
                )
            finally:
                os.chdir(original_dir)

    def test_package_plugin_repo_url_from_config(self):
        """Test plugin_repo_url from config repository_plugin_url."""
        self.assertEqual(
            "https://qgis.github.io/qgis-plugin-ci/",
            self.qgis_plugin_config_params.plugin_repo_url,
        )

        archive_name = self.qgis_plugin_config_params.archive_name(
            self.qgis_plugin_config_params.plugin_path, RELEASE_VERSION_TEST
        )
        original_dir = Path().cwd()
        with TemporaryDirectory() as tmp_dir:
            try:
                os.chdir(tmp_dir)
                xml_path = create_plugin_repo(
                    parameters=self.qgis_plugin_config_params,
                    release_version=RELEASE_VERSION_TEST,
                    release_tag=RELEASE_VERSION_TEST,
                    archive=archive_name,
                    plugin_repo_url=self.qgis_plugin_config_params.plugin_repo_url,
                )
                content = Path(xml_path).read_text(encoding="utf-8")
                expected_url = f"https://qgis.github.io/qgis-plugin-ci/{archive_name}"
                self.assertIn(
                    expected_url,
                    content,
                    "Download hyperlink must be the one set in config file",
                )
            finally:
                os.chdir(original_dir)


class TestUploadPluginWithToken(unittest.TestCase):
    def setUp(self):
        import tempfile
        import zipfile

        self.tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
        with zipfile.ZipFile(self.tmp.name, "w") as zf:
            zf.writestr("my_plugin/metadata.txt", "name=My Plugin\nversion=1.0.0\n")
        self.tmp.close()

    def tearDown(self):
        import os

        os.unlink(self.tmp.name)

    @unittest.mock.patch("qgispluginci.release.requests.post")
    def test_auto_approve_sends_field(self, mock_post):
        mock_post.return_value = unittest.mock.MagicMock(status_code=200)
        upload_plugin_to_osgeo_with_token(
            self.tmp.name, "my_plugin", "token123", auto_approve=True
        )
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["data"], {"auto_approve_after_scan": "true"})

    @unittest.mock.patch("qgispluginci.release.requests.post")
    def test_no_auto_approve_omits_field(self, mock_post):
        mock_post.return_value = unittest.mock.MagicMock(status_code=200)
        upload_plugin_to_osgeo_with_token(
            self.tmp.name, "my_plugin", "token123", auto_approve=False
        )
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["data"], {})


if __name__ == "__main__":
    unittest.main()
