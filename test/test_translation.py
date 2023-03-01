#! /usr/bin/env python

# standard library
import logging
import os
import unittest

# 3rd party
import yaml

# project
from qgispluginci.parameters import Parameters
from qgispluginci.translation import Translation

# Tests
from .utils import can_skip_test

# Logging
logger = logging.getLogger(__name__)

# Ensuring proper ordering for tests sensitive to state
unittest.TestLoader.sortTestMethodsUsing = None


class TestTranslation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the test case"""
        with open(".qgis-plugin-ci") as f:
            arg_dict = yaml.safe_load(f)
        cls.parameters = Parameters(arg_dict)
        cls.tx_api_token = os.getenv("tx_api_token")
        assert cls.tx_api_token

    def setUp(self):
        """Initialize the next test method (run before every test method)"""
        self.t = Translation(self.parameters, tx_api_token=self.tx_api_token)

    def tearDown(self):
        self.t.tx_client.delete_project()
        """
        try:
            self.t.tx_client.delete_team(f"{self.parameters.project_slug}-team")
        except PyTransifexException as error:
            logger.debug(error)
        """

    @unittest.skipIf(can_skip_test(), "Missing tx_api_token")
    def test_creation(self):
        """
        Translation initialized from setUp, so we 'fake' a new test
        by tearing it down
        """
        self.t = Translation(self.parameters, tx_api_token=self.tx_api_token)
        self.t.tx_client.delete_project()
        self.assertFalse(self.t.tx_client.project_exists(self.parameters.project_slug))
        self.t = Translation(self.parameters, tx_api_token=self.tx_api_token)
        self.assertTrue(self.t.tx_client.project_exists(self.parameters.project_slug))
        self.assertEqual(len(self.t.tx_client.list_resources()), 1)

    @unittest.skipIf(can_skip_test(), "Missing tx_api_token")
    def test_push(self):
        self.t.update_strings()
        self.t.push()

    @unittest.skipIf(can_skip_test(), "Missing tx_api_token")
    def test_pull(self):
        self.t.pull()
        self.t.compile_strings()


if __name__ == "__main__":
    unittest.main()
