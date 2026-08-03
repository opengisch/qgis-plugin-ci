#! /usr/bin/env python

# standard
import unittest
from datetime import datetime
from pathlib import Path

# Project
from qgispluginci.exceptions import ConfigurationNotFound
from qgispluginci.parameters import Parameters


class TestParameters(unittest.TestCase):
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

    def test_auto_approve_defaults_to_true(self):
        """auto_approve must default to True when not set in the config file."""
        parameters = Parameters.make_from(
            path_to_config_file=Path("test/fixtures/.qgis-plugin-ci")
        )
        self.assertTrue(parameters.auto_approve)

    def test_auto_approve_from_config(self):
        """auto_approve must be read from the config file when set."""
        parameters = Parameters.make_from(
            path_to_config_file=Path(
                "test/fixtures/auto_approve_disabled/.qgis-plugin-ci"
            )
        )
        self.assertFalse(parameters.auto_approve)
