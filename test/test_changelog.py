#! python3  # noqa E265

"""
    Usage from the repo root folder:

    .. code-block:: bash
        # for whole test
        python -m unittest test.test_changelog
"""

import unittest

from qgispluginci.changelog import ChangelogParser
from qgispluginci.parameters import CHANGELOG_REGEXP


class TestChangelog(unittest.TestCase):
    def test_changelog_parser(self):
        """ Test we can parse a changelog with a regex. """
        self.assertTrue(ChangelogParser.has_changelog())
        parser = ChangelogParser(CHANGELOG_REGEXP)
        self.assertIsNone(parser.content("0.0.0"), "")

        expected = (
            "* Tag using a wrong format DD/MM/YYYY according to Keep A Changelog\n"
            '* Tag without "v" prefix\n'
            "* Add a CHANGELOG.md file for testing"
        )
        self.assertEqual(parser.content("0.1.2"), expected)

        expected = (
            "\n "
            "Version 0.1.2 :\n "
            "* Tag using a wrong format DD/MM/YYYY according to Keep A Changelog\n "
            '* Tag without "v" prefix\n '
            "* Add a CHANGELOG.md file for testing\n"
            "\n"
        )
        self.assertEqual(parser.last_items(1), expected)

        expected = """
 Version 0.1.2 :
 * Tag using a wrong format DD/MM/YYYY according to Keep A Changelog
 * Tag without "v" prefix
 * Add a CHANGELOG.md file for testing

 Version v0.1.1 :
 * Tag using a correct format YYYY-MM-DD according to Keep A Changelog
 * Tag with a "v" prefix to check the regular expression
 * Previous version

 Version 0.1.0 :
 * Very old version

"""
        self.assertEqual(parser.last_items(3), expected)

    def test_changelog_latest(self):
        """Test against the latest special option value. \
        See: https://github.com/opengisch/qgis-plugin-ci/pull/33
        """
        self.assertTrue(ChangelogParser.has_changelog())
        parser = ChangelogParser(CHANGELOG_REGEXP)
        expected_latest = (
            "* Tag using a wrong format DD/MM/YYYY according to Keep A Changelog\n"
            '* Tag without "v" prefix\n'
            "* Add a CHANGELOG.md file for testing"
        )
        print(parser.content("latest"))
        self.assertEqual(expected_latest, parser.content("latest"))


if __name__ == "__main__":
    unittest.main()
