# Settings

The plugin must have a configuration, located at the top directory:

- either you use a `.qgis-plugin-ci` file
- or you use a `[qgis-plugin-ci]` section in a `setup.cfg` file (which is used by many other tool).

In the configuration, you should at least provide the following configuration:

- `plugin_path`, the folder where the source code is located

Side note, the plugin path shouldn't have any dash character.

You can find a template `.qgis-plugin-ci` in this repository.
You can read the docstring of the file `qgispluginci/parameters.py`
to know parameters which are available in the file.

## Examples

- `.qgis-plugin-ci`

```yaml
plugin_path: qgis_plugin_ci_testing
github_organization_slug: opengisch
project_slug: qgis-plugin-ci
```

- `setup.cfg`

```ini
[qgis-plugin-ci]
plugin_path = QuickOSM
github_organization_slug = 3liz
project_slug = QuickOSM
```
