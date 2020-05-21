#! /usr/bin/env python

import os
import unittest
import yaml
import filecmp
import urllib.request
from tempfile import mkstemp
from github import Github, GithubException
from zipfile import ZipFile

from pytransifex.exceptions import PyTransifexException

from qgispluginci.parameters import Parameters
from qgispluginci.release import release
from qgispluginci.translation import Translation
from qgispluginci.exceptions import GithubReleaseNotFound
from qgispluginci.utils import replace_in_file

# if change, also update on .travis.yml and CHANGELOG.md
RELEASE_VERSION_TEST = '0.1.2'


class TestRelease(unittest.TestCase):

    def setUp(self):
        arg_dict = yaml.safe_load(open(".qgis-plugin-ci"))
        self.parameters = Parameters(arg_dict)
        self.transifex_token = os.getenv('transifex_token')
        self.github_token = os.getenv('github_token')
        self.repo = None
        self.t = None
        if self.github_token:
            print('init Github')
            self.repo = Github(self.github_token).get_repo('opengisch/qgis-plugin-ci')
        self.clean_assets()

    def tearDown(self):
        self.clean_assets()

    def clean_assets(self):
        if self.repo:
            rel = None
            try:
                rel = self.repo.get_release(id=RELEASE_VERSION_TEST)
            except GithubException as e:
                raise GithubReleaseNotFound('Release {} not found'.format(RELEASE_VERSION_TEST))
            if rel:
                print('deleting release assets')
                for asset in rel.get_assets():
                    print('  delete {}'.format(asset.name))
                    asset.delete_asset()
        if self.t:
            try:
                self.t._t.delete_project(self.parameters.project_slug)
            except PyTransifexException:
                pass
            try:
                self.t._t.delete_team('{}-team'.format(self.parameters.project_slug))
            except PyTransifexException:
                pass

    def test_release(self):
        release(self.parameters, RELEASE_VERSION_TEST)

    def test_release_with_transifex(self):
        assert self.transifex_token is not None
        t = Translation(self.parameters, transifex_token=self.transifex_token)
        release(self.parameters, RELEASE_VERSION_TEST, transifex_token=self.transifex_token)

    def test_release_upload_github(self):
        release(self.parameters, RELEASE_VERSION_TEST, github_token=self.github_token, upload_plugin_repo_github=True)

        # check the custom plugin repo
        _, xml_repo = mkstemp(suffix='.xml')
        url = 'https://github.com/opengisch/qgis-plugin-ci/releases/download/{}/plugins.xml'.format(RELEASE_VERSION_TEST)
        print('retrieve repo from {}'.format(url))
        urllib.request.urlretrieve(url, xml_repo)
        replace_in_file(xml_repo, r'<update_date>[\w-]+<\/update_date>', '<update_date>__TODAY__</update_date>')
        if not filecmp.cmp('test/plugins.xml.expected', xml_repo, shallow=False):
            import difflib
            text1 = open('test/plugins.xml.expected').readlines()
            text2 = open(xml_repo).readlines()
            self.assertFalse(True, '\n'.join(difflib.unified_diff(text1, text2)))

        # compare archive file size
        gh_release = self.repo.get_release(id=RELEASE_VERSION_TEST)
        archive_name = self.parameters.archive_name(RELEASE_VERSION_TEST)
        fs = os.path.getsize(archive_name)
        print('size: ', fs)
        self.assertGreater(fs, 0, 'archive file size must be > 0')
        found = False
        for a in gh_release.get_assets():
            if a.name == archive_name:
                found = True
                self.assertEqual(fs, a.size, 'asset size doesn\'t march archive size.')
                break
        self.assertTrue(found, 'asset not found')

    def test_release_changelog(self):
        """ Test about the changelog in the metadata.txt. """
        expected = b'changelog=\n Version 0.1.2:\n * Add a CHANGELOG.md file for testing\n'

        # Include a changelog
        release(self.parameters, RELEASE_VERSION_TEST)
        archive_name = self.parameters.archive_name(RELEASE_VERSION_TEST)
        with ZipFile(archive_name, 'r') as zip_file:
            data = zip_file.read('qgis_plugin_ci_testing/metadata.txt')
            self.assertGreater(data.find(expected), 0)


if __name__ == '__main__':
    unittest.main()
