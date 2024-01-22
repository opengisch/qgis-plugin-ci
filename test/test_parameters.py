#! /usr/bin/env python

# standard
import unittest
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
        self.assertEqual("qgis_plugin_CI_testing", parameters.plugin_path)
        self.assertEqual("CHANGELOG.md", parameters.changelog_path)
