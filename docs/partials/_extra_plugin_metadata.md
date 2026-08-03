<!-- markdownlint-disable MD041 -->
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

This same section can also hold **static configuration options**
(e.g. `github_organization_slug`, `timezone`) when the main config file contains
only `plugin_path`. See [Minimal configuration with `metadata.txt`](../configuration/options.md#combining-minimal-configuration-with-metadata-txt).

:::
