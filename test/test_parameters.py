#! /usr/bin/env python

# standard
import unittest

# Project
from qgispluginci.parameters import Parameters


class TestParameters(unittest.TestCase):
    def test_changelog_parameters(self):
        """Test parameters for changelog command."""
        # For the changelog command, the configuration file is optional.
        parameters = Parameters.make_from(args={}, optional_configuration=True)
        self.assertEqual("CHANGELOG.md", parameters.changelog_path)
        self.assertIsNone(parameters.plugin_path)
