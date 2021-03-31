#! python3  # noqa E265

"""
    Usage from the repo root folder:

    .. code-block:: bash
        # for whole tests
        python -m unittest test.test_changelog
        # for specific test
        python -m unittest test.test_changelog.TestChangelog.test_has_changelog
"""

# standard library
import unittest
from pathlib import Path

# project
from qgispluginci.changelog import ChangelogParser
from qgispluginci.parameters import CHANGELOG_REGEXP

# ############################################################################
# ########## Globals #############
# ################################


class TestChangelog(unittest.TestCase):
    def test_has_changelog(self):
        """Test changelog path logic."""
        # using this repository as parent folder
        self.assertTrue(ChangelogParser.has_changelog())
        self.assertIsInstance(ChangelogParser.CHANGELOG_FILEPATH, Path)

        # using the fixture subfolder as string
        self.assertTrue(ChangelogParser.has_changelog(parent_folder="test/fixtures"))
        self.assertIsInstance(ChangelogParser.CHANGELOG_FILEPATH, Path)

        # using the fixture subfolder as pathlib.Path
        self.assertTrue(
            ChangelogParser.has_changelog(parent_folder=Path("test/fixtures"))
        )
        self.assertIsInstance(ChangelogParser.CHANGELOG_FILEPATH, Path)

        # with a path to a file, must raise a type error
        with self.assertRaises(TypeError):
            ChangelogParser.has_changelog(parent_folder=Path(__file__))
        self.assertIsNone(ChangelogParser.CHANGELOG_FILEPATH, None)

        # with a path to a folder which doesn't exist, must raise a file exists error
        with self.assertRaises(FileExistsError):
            ChangelogParser.has_changelog(parent_folder=Path("imaginary_path"))

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
