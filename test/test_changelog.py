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
import tempfile
import unittest
from pathlib import Path

# project
from qgispluginci.changelog import ChangelogParser
from qgispluginci.version_note import VersionNote

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
        with self.assertRaises(SystemExit):
            ChangelogParser.has_changelog(parent_folder=Path(__file__))
        self.assertIsNone(ChangelogParser.CHANGELOG_FILEPATH, None)

        # with a path to a folder which doesn't exist, must raise a file exists error
        with self.assertRaises(SystemExit):
            ChangelogParser.has_changelog(parent_folder=Path("imaginary_path"))

    def test_changelog_content(self):
        """Test version content from changelog."""
        # parser
        parser = ChangelogParser(parent_folder="test/fixtures")
        self.assertIsInstance(parser.CHANGELOG_FILEPATH, Path)

        # Unreleased doesn't count
        self.assertEqual(7, len(parser._parse()))

        # This version doesn't exist
        self.assertIsNone(parser.content("0.0.0"))

        expected_checks = {
            "10.1.0-beta1": (
                "- This is the latest documented version in this changelog\n"
                "- The changelog module is tested against these lines\n"
                "- Be careful modifying this file"
            ),
            "10.1.0-alpha1": (
                "- This is a version with a prerelease in this changelog\n"
                "- The changelog module is tested against these lines\n"
                "- Be careful modifying this file"
                # "\n" TODO Fixed section is missing
                # "- trying with a subsection in a version note"
            ),
            "10.0.1": "- End of year version",
            "10.0.0": "- A\n- B\n- C",
            "9.10.1": "- D\n- E\n- F",
            "v0.1.1": (
                '* Tag with a "v" prefix to check the regular expression\n'
                "* Previous version"
            ),
            "0.1.0": "* Very old version",
        }
        for version, expected in expected_checks.items():
            with self.subTest(i=version):
                self.assertEqual(parser.content(version), expected)

    def test_changelog_content_latest(self):
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

        self.assertEqual("10.1.0-beta1", parser.latest_version())

    def test_changelog_content_ci_fake(self):
        """Test specific fake version used in tests."""
        parser = ChangelogParser()
        fake_version_content = parser.content(tag="0.1.2")

        # expected result
        expected = (
            "(This version note is used in unit-tests)\n\n"
            '* Tag without "v" prefix\n'
            "* Add a CHANGELOG.md file for testing"
        )

        self.assertIsInstance(fake_version_content, str)
        self.assertEqual(expected, fake_version_content)

    def test_different_changelog_file(self):
        """Test against a different changelog filename."""
        old = Path("test/fixtures/CHANGELOG.md")
        new_folder = Path(tempfile.mkdtemp())
        new_path = new_folder / Path("CHANGELOG-branch-X.md")
        self.assertFalse(new_path.exists())

        new_path.write_text(old.read_text())

        self.assertTrue(
            ChangelogParser.has_changelog(
                parent_folder=new_folder,
                changelog_path=new_path,
            )
        )

    def test_changelog_last_items(self):
        """Test last items from changelog."""
        # on fixture changelog
        parser = ChangelogParser(parent_folder="test/fixtures")
        last_items = parser.last_items(3)
        self.assertIsInstance(last_items, str)

        # on repository changelog
        parser = ChangelogParser()
        last_items = parser.last_items(3)
        self.assertIsInstance(last_items, str)

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

    def test_version_note_tuple(self):
        """Test the version note tuple."""
        parser = ChangelogParser(parent_folder="test/fixtures")

        version = parser._version_note("0.0.0")
        self.assertIsNone(version)

        version = parser._version_note("10.1.0-beta1")
        self.assertEqual("10", version.major)
        self.assertEqual("1", version.minor)
        self.assertEqual("0", version.patch)
        self.assertEqual("", version.url)
        self.assertEqual("beta1", version.prerelease)
        self.assertTrue(version.is_prerelease)
        self.assertEqual("", version.separator)  # Not sure what is the separator
        self.assertEqual("2021/02/08", version.date)
        self.assertEqual(
            (
                "- This is the latest documented version in this changelog\n"
                "- The changelog module is tested against these lines\n"
                "- Be careful modifying this file"
            ),
            version.text,
        )

        version = parser._version_note("10.0.1")
        self.assertEqual("", version.prerelease)
        self.assertFalse(version.is_prerelease)


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
