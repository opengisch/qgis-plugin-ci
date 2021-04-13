#! /usr/bin/env python

# standard library
import os
import unittest

# 3rd party
import yaml
from pytransifex.exceptions import PyTransifexException
from utils import can_skip_test

# project
from qgispluginci.parameters import Parameters
from qgispluginci.translation import Translation


class TestTranslation(unittest.TestCase):
    def setUp(self):
        arg_dict = yaml.safe_load(open(".qgis-plugin-ci"))
        self.parameters = Parameters(arg_dict)
        self.transifex_token = os.getenv("transifex_token")
        self.assertIsNotNone(self.transifex_token)
        self.t = Translation(self.parameters, transifex_token=self.transifex_token)

    def tearDown(self):
        try:
            self.t._t.delete_project(self.parameters.project_slug)
        except PyTransifexException:
            pass
        try:
            self.t._t.delete_team("{}-team".format(self.parameters.project_slug))
        except PyTransifexException:
            pass

    @unittest.skipIf(can_skip_test(), "Missing transifex_token")
    def test_creation(self):
        self.t = Translation(self.parameters, transifex_token=self.transifex_token)
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
