#! /usr/bin/env python

import unittest
import yaml
import os

from qgispluginci.parameters import Parameters
from qgispluginci.translation import Translation
from pytransifex.exceptions import PyTransifexException


class TestTranslation(unittest.TestCase):

    def setUp(self):
        arg_dict = yaml.safe_load(open(".qgis-plugin-ci"))
        self.parameters = Parameters(arg_dict)
        self.transifex_token = os.getenv('transifex_token')
        assert self.transifex_token is not None
        self.t = Translation(self.parameters, transifex_token=self.transifex_token)

    def tearDown(self):
        try:
            self.t._t.delete_project(self.parameters.project_slug)
        except PyTransifexException:
            pass
        try:
            self.t._t.delete_team('{}-team'.format(self.parameters.project_slug))
        except PyTransifexException:
            pass

    def test_creation(self):
        self.t = Translation(self.parameters, transifex_token=self.transifex_token)
        self.tearDown()
        self.t = Translation(self.parameters, transifex_token=self.transifex_token)

    def test_pull(self):
        self.t.pull()
        self.t.compile_strings()

    def test_push(self):
        self.t.update_strings()
        self.t.push()


if __name__ == '__main__':
    unittest.main()
