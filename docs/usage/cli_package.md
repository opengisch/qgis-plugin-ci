# Package

This command is not specific to the hosting platform (GitLab, GitHub…)

```bash
usage: qgis-plugin-ci package [-h]
                              [--transifex-token TRANSIFEX_TOKEN]
                              [--plugin-repo-url PLUGIN_REPO_URL]
                              [--allow-uncommitted-changes]
                              release_version

positional arguments:
  release_version       The version to be released

optional arguments:
  -h, --help            show this help message and exit
  --transifex-token TRANSIFEX_TOKEN
                        The Transifex API token. If specified translations
                        will be pulled and compiled.
  -u --plugin-repo-url PLUGIN_REPO_URL
                        If specified, a XML repository file will be created in the current directory, the zip URL will use this parameter.
  -c --allow-uncommitted-changes
                        If omitted, uncommitted changes are not allowed before
                        packaging. If specified and some changes are detected,
                        a hard reset on a stash create will be used to revert
                        changes made by qgis-plugin-ci.
  -d --disable-submodule-update
                        If omitted, a git submodule is updated. If specified, git submodules will not be updated/initialized before packaging.

```

## Additional metadata

When packaging the plugin, some extra metadata information can be added if these keys are present in the `metadata.txt`:

* `commitNumber=` : the commit number in the branch otherwise 1 on a tag
* `commitSha1=` : the commit ID
* `dateTime=` : the date time in UTC format when the packaging is done

:::{tip}
These extra parameters are specific to QGIS Plugin CI, so it's strongly recommended storing them below a dedicated section:

```ini
[tool:qgis-plugin-ci]
commitNumber=
commitSha1=
dateTime=
```

:::
