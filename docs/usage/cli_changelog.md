# Changelog (CLI)

By default, the changelog command will work with a file formatted like [this changelog.md file](./CHANGELOG.md).

If your format is different, you must use a different `changelog_regexp` expression to parse it in your settings.

```bash
usage: qgis-plugin-ci changelog [-h] release_version

positional arguments:
  release_version  The version to be released. If nothing is speficied, the latest
                   version specified into the changelog is used.

optional arguments:
  -h, --help       show this help message and exit
```
