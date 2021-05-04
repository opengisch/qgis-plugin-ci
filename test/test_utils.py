import unittest

from qgispluginci.utils import parse_tag
from qgispluginci.version_note import VersionNote


class TestUtils(unittest.TestCase):
    def test_version_note_from_tag(self):
        """Test to parse a tag and check the version note."""

        version = parse_tag("10.1.0-beta1")
        self.assertIsInstance(version, VersionNote)
        self.assertEqual("10", version.major)
        self.assertEqual("1", version.minor)
        self.assertEqual("0", version.patch)
        self.assertEqual("beta1", version.prerelease)
        self.assertTrue(version.is_prerelease)

        version = parse_tag("3.4.0-rc.2")
        self.assertIsInstance(version, VersionNote)
        self.assertEqual("3", version.major)
        self.assertEqual("4", version.minor)
        self.assertEqual("0", version.patch)
        self.assertEqual("rc.2", version.prerelease)
        self.assertTrue(version.is_prerelease)

        version = parse_tag("10.1.0")
        self.assertIsInstance(version, VersionNote)
        self.assertEqual("10", version.major)
        self.assertEqual("1", version.minor)
        self.assertEqual("0", version.patch)
        self.assertIsNone(version.prerelease)
        self.assertFalse(version.is_prerelease)

        version = parse_tag("v10.1.0")
        self.assertIsInstance(version, VersionNote)
        self.assertEqual("v10", version.major)
        self.assertEqual("1", version.minor)
        self.assertEqual("0", version.patch)
        self.assertIsNone(version.prerelease)
        self.assertFalse(version.is_prerelease)

        # Not following https://semver.org/, we can't guess
        version = parse_tag("10.1")
        self.assertIsInstance(version, VersionNote)
        self.assertIsNone(version.major)
        self.assertIsNone(version.minor)
        self.assertIsNone(version.patch)
        self.assertIsNone(version.prerelease)
        self.assertFalse(version.is_prerelease)


if __name__ == "__main__":
    unittest.main()
