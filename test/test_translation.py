#! /usr/bin/env python

# standard library
import os
import unittest

# 3rd party
import yaml
from pytransifex.exceptions import PyTransifexException

# project
from qgispluginci.parameters import Parameters
from qgispluginci.translation import Translation

# Tests
from .utils import can_skip_test


class TestTranslation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the test case"""
        with open(".qgis-plugin-ci") as f:
            arg_dict = yaml.safe_load(f)
        cls.parameters = Parameters(arg_dict)
        cls.transifex_token = os.getenv("transifex_token")
        assert cls.transifex_token

    def setUp(self):
        """Initialize the next test method (run between every test method)"""
        self.t = Translation(self.parameters, transifex_token=self.transifex_token)

    def tearDown(self):
        try:
            self.t._t.delete_project(self.parameters.project_slug)
        except PyTransifexException:
            pass
        try:
            self.t._t.delete_team(f"{self.parameters.project_slug}-team")
        except PyTransifexException:
            pass

    @unittest.skipIf(can_skip_test(), "Missing transifex_token")
    def test_creation(self):
        """
        Translation initialized from setUp, so we 'fake' a new test
        by tearing it down
        """
        self.tearDown()
        self.t = Translation(self.parameters, transifex_token=self.transifex_token)

    @unittest.skipIf(can_skip_test(), "Missing transifex_token")
    def test_pull(self):
        self.t.pull()
        self.t.compile_strings()

    @unittest.skipIf(can_skip_test(), "Missing transifex_token")
    def test_push(self):
        self.t.update_strings()
        self.t.push()


if __name__ == "__main__":
    unittest.main()
