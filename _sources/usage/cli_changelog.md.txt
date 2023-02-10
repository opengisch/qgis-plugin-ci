# Changelog (CLI)

Manipulate `CHANGELOG.md` file, extracting relevant information.  
Used within the [package](cli_package) and [release](cli_release) commands to populate the `metadata.txt` and the GitHub Release description.

By default, the script will look for a file `CHANGELOG.md` in the root folder.
But you can specify a specific file path with `changelog_path` in the configuration file.
For instance:

```ini
changelog_path=CHANGELOG-3.4.md
```

or

```ini
changelog_path=subfolder/CHANGELOG.md
```

## Command help

```bash
usage: qgis-plugin-ci changelog [-h] release_version

positional arguments:
  release_version  The version to be released. If nothing is speficied, the latest
                   version specified into the changelog is used.

optional arguments:
  -h, --help       show this help message and exit
```

## Requirements

The `CHANGELOG.md` file must follow the convention [Keep A Changelog](https://keepachangelog.com/). For example, see this [repository changelog](https://github.com/opengisch/qgis-plugin-ci/blob/master/CHANGELOG.md).

## Use cases

- Extract the `CHANGELOG.md` content and copy it into the `changelog` section within plugin `metadata.txt`
- Extract the `n` latest versions from `CHANGELOG.md` into `metadata.txt`
- Get the latest version release note

## Examples

### Extract changelog for latest version

```bash
$ qgis-plugin-ci changelog latest
- Separate python files and UI files in the temporary PRO file (#29)
```
