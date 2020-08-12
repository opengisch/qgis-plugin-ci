#! /usr/bin/env python

import unittest

from qgispluginci.changelog import ChangelogParser
from qgispluginci.parameters import CHANGELOG_REGEXP


class TestChangelog(unittest.TestCase):

    def test_changelog_parser(self):
        """ Test we can parse a changelog with a regex. """
        self.assertTrue(ChangelogParser.has_changelog())
        parser = ChangelogParser(CHANGELOG_REGEXP)
        self.assertIsNone(parser.content('0.0.0'), '')
        self.assertEqual(parser.content('0.1.2'), '* Tag without "v" prefix\n* Add a CHANGELOG.md file for testing')

        expected = '\n Version 0.1.2:\n * Tag without "v" prefix\n * Add a CHANGELOG.md file for testing\n\n'
        self.assertEqual(parser.last_items(1), expected)

        expected = ("""
 Version 0.1.2:
 * Tag without "v" prefix
 * Add a CHANGELOG.md file for testing

 Version v0.1.1:
 * Tag with a "v" prefix to check the regular expression
 * Previous version

 Version 0.1.0:
 * Very old version

""")
        self.assertEqual(parser.last_items(3), expected)


if __name__ == '__main__':
    unittest.main()
