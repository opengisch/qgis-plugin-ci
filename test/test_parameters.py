#! /usr/bin/env python

# standard
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

# Project
from qgispluginci.exceptions import ConfigurationNotFound
from qgispluginci.parameters import Parameters


class TestParameters(unittest.TestCase):
    # -- helpers ----------------------------------------------------------

    @staticmethod
    def _minimal_metadata(plugin_dir: Path) -> None:
        """Write a valid metadata.txt with all mandatory fields."""
        (plugin_dir / "metadata.txt").write_text(
            data="[general]\n"
            "name=Quicui\n"
            "about=Lorem ipsum GIS ergo sum\n"
            "description=Test plugin\n"
            "qgisMinimumVersion=3.44.10\n"
            "author=Former Esri repentant\n"
            "homepage=https://opengisch.github.io/qgis-plugin-ci/\n"
            "tracker=https://github.com/opengisch/qgis-plugin-ci/issues\n"
            "repository=https://github.com/opengisch/qgis-plugin-ci\n",
            encoding="UTF-8",
        )

    def test_changelog_parameters(self):
        """Test parameters for changelog command."""
        # For the changelog command, the configuration file is optional.
        # It mustn't raise an exception
        parameters = Parameters.make_from(args={}, optional_configuration=True)
        self.assertIsNone(parameters.plugin_path)
        self.assertEqual("CHANGELOG.md", parameters.changelog_path)

    def test_global_parameters(self):
        """Test global parameters."""
        # A configuration file must exist.
        with self.assertRaises(ConfigurationNotFound):
            Parameters.make_from(
                args={}, path_to_config_file=Path("does-not-exist.yml")
            )

        # Existing configuration file
        parameters = Parameters.make_from(
            args={}, path_to_config_file=Path("test/fixtures/pyproject.toml")
        )
        self.assertIsInstance(parameters.create_datetime, datetime)
        self.assertIsNotNone(parameters.create_datetime.tzinfo)

        self.assertEqual("qgis_plugin_CI_testing", parameters.plugin_path)
        self.assertEqual("CHANGELOG.md", parameters.changelog_path)
        self.assertIsNone(parameters.plugin_repo_url)

    def test_plugin_repo_url_from_config(self):
        """--plugin-repo-url must be read from config file (repository_plugin_url)."""
        parameters = Parameters.make_from(
            path_to_config_file=Path("test/fixtures/.qgis-plugin-ci")
        )
        self.assertEqual(
            "https://qgis.github.io/qgis-plugin-ci/", parameters.plugin_repo_url
        )

    def test_metadata_txt_ci_section_merged_when_plugin_path_only(self):
        """[tool:qgis-plugin-ci] from metadata.txt is merged when config only defines plugin_path."""
        original_dir = Path.cwd()
        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                os.chdir(tmp_dir)
                plugin_dir = Path(tmp_dir) / "my_plugin"
                plugin_dir.mkdir()
                self._minimal_metadata(plugin_dir)
                # Append [tool:qgis-plugin-ci] section
                with (plugin_dir / "metadata.txt").open("a") as fh:
                    fh.write(
                        "\n[tool:qgis-plugin-ci]\n"
                        "github_organization_slug=my_org\n"
                        "project_slug=my_project\n"
                        "timezone=Europe/Paris\n"
                    )
                config_file = Path(tmp_dir) / ".qgis-plugin-ci"
                config_file.write_text("plugin_path: my_plugin\n")

                parameters = Parameters.make_from(path_to_config_file=config_file)

                self.assertEqual("my_org", parameters.github_organization_slug)
                self.assertEqual("my_project", parameters.project_slug)
                self.assertEqual("Europe/Paris", parameters.timezone)
            finally:
                os.chdir(original_dir)

    def test_missing_ci_section_in_metadata_txt_logs_warning(self):
        """A warning is logged when metadata.txt exists but has no [tool:qgis-plugin-ci] section."""
        original_dir = Path.cwd()
        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                os.chdir(tmp_dir)
                plugin_dir = Path(tmp_dir) / "my_plugin"
                plugin_dir.mkdir()
                self._minimal_metadata(plugin_dir)
                config_file = Path(tmp_dir) / ".qgis-plugin-ci"
                config_file.write_text("plugin_path: my_plugin\n")

                with self.assertLogs("qgispluginci.parameters", level="WARNING") as cm:
                    Parameters.make_from(path_to_config_file=config_file)

                self.assertTrue(
                    any("tool:qgis-plugin-ci" in msg for msg in cm.output),
                    "Expected a warning mentioning [tool:qgis-plugin-ci]",
                )
            finally:
                os.chdir(original_dir)

    def test_missing_metadata_txt_logs_warning(self):
        """A warning is logged when metadata.txt itself is absent."""
        original_dir = Path.cwd()
        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                os.chdir(tmp_dir)
                config_file = Path(tmp_dir) / ".qgis-plugin-ci"
                config_file.write_text("plugin_path: ghost_plugin\n")

                with self.assertLogs("qgispluginci.parameters", level="WARNING") as cm:
                    with self.assertRaises(FileNotFoundError):
                        Parameters.make_from(path_to_config_file=config_file)

                self.assertTrue(
                    any(
                        "ghost_plugin" in msg and "metadata.txt" in msg
                        for msg in cm.output
                    ),
                    "Expected a warning mentioning the missing metadata.txt path",
                )
            finally:
                os.chdir(original_dir)

    def test_metadata_txt_not_checked_when_config_has_extra_keys(self):
        """metadata.txt is not consulted when the config file has more than plugin_path."""
        # Fixture has github_organization_slug in addition to plugin_path → new block must NOT trigger.
        # If it were triggered and merged a metadata.txt section with conflicting values,
        # the assertion below would still pass (config file takes priority), but any warning
        # log would betray the wrong code path.
        with self.assertNoLogs("qgispluginci.parameters", level="WARNING"):
            parameters = Parameters.make_from(
                path_to_config_file=Path("test/fixtures/.qgis-plugin-ci")
            )
        self.assertEqual("opengisch", parameters.github_organization_slug)
