"""Changelog parser.

Following nearly https://keepachangelog.com/en/1.0.0/
"""

import re

from os.path import isfile


class ChangelogParser:

    @staticmethod
    def has_changelog():
        return isfile('CHANGELOG.md')

    def __init__(self, regexp):
        self.regexp = regexp

    def _parse(self):
        if not self.has_changelog():
            return ''

        f = open('CHANGELOG.md', "r")
        content = f.read()
        f.close()
        return re.findall(self.regexp, content, flags=re.MULTILINE | re.DOTALL)

    def last_items(self, count):
        """Content to add in the metadata.txt.

        :param count: Maximum number of tags to include in the file.
        """
        changelog_content = self._parse()
        if not changelog_content:
            return ''

        count = int(count)
        output = '\n'
        for version, date, items in changelog_content[0:count]:
            output += ' Version {}:\n'.format(version)
            for item in items.split('\n'):
                if item:
                    output += ' {}\n'.format(item)
            output += '\n'
        return output

    def content(self, tag):
        """Content to add in a release according to a tag."""
        changelog_content = self._parse()
        for version, date, items in changelog_content:
            if version == tag:
                return items.strip()
