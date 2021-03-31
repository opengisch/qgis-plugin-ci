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
from qgispluginci.changelog import ChangelogParser, VersionNote

# ############################################################################
# ########## Classes #############
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
        parser = ChangelogParser(parent_folder="test/fixtures")
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

    def test_changelog_content(self):
        """Test version content from changelog."""
        # parser
        parser = ChangelogParser(parent_folder="test/fixtures")
        self.assertIsInstance(parser.CHANGELOG_FILEPATH, Path)

        # checks
        self.assertIsNone(parser.content("0.0.0"))
        self.assertIsInstance(parser.content("10.1.0-alpha1"), str)

    def test_changelog_last_items(self):
        """Test last items from changelog."""
        parser = ChangelogParser(parent_folder="test/fixtures")

        last_items = parser.last_items(3)
        self.assertIsInstance(last_items, str)

    def test_changelog_latest(self):
        """Test against the latest special option value. \
        See: https://github.com/opengisch/qgis-plugin-ci/pull/33
        """
        # expected result
        expected_latest = (
            "- This is the latest documented version in this changelog\n"
            "- The changelog module is tested against these lines\n"
            "- Be careful modifying this file"
        )

        # get latest
        parser = ChangelogParser(parent_folder="test/fixtures")
        self.assertEqual(expected_latest, parser.content("latest"))

    def test_changelog_version_note(self):
        """Test version note named tuple structure and mechanisms."""
        # parser
        parser = ChangelogParser(parent_folder="test/fixtures")
        self.assertIsInstance(parser.CHANGELOG_FILEPATH, Path)

        # content parsed
        changelog_content = parser._parse()
        self.assertEqual(len(changelog_content), 7)

        # loop on versions
        for version in changelog_content:
            version_note = VersionNote(*version)
            self.assertIsInstance(version_note.date, str)
            self.assertTrue(hasattr(version_note, "is_prerelease"))
            self.assertTrue(hasattr(version_note, "version"))
            if len(version_note.prerelease):
                self.assertEqual(version_note.is_prerelease, True)


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
