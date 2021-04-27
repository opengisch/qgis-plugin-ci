# Settings

The plugin must have a configuration, located at the top directory:

- either you use a `.qgis-plugin-ci` YAML file
- or you use a `[qgis-plugin-ci]` section in a `setup.cfg` file (which is used by many other tools).

In the configuration, you should at least provide the following configuration:

- `plugin_path`, the folder where the source code is located

Side note, the plugin path shouldn't have any dash character.

You can find a template `.qgis-plugin-ci` in this repository.
You can read the docstring of the [Parameters module](/_apidoc/qgispluginci.parameters) to know parameters which are available in the file.

## Conventions

QGIS-Plugin-CI is best served if you use these two conventions :

* [Semantic versioning](https://semver.org/)
* [Keep A Changelog](https://keepachangelog.com)

## Options

| Name | Required | Description | Example |
| :--- | :------: | :---------- | :------ |
| `github_organization_slug` | no | The *organization* slug on SCM host (e.g. Github) and translation platform (e.g. Transifex).<br/>Not required when running on Travis since deduced from `$TRAVIS_REPO_SLUG`environment variable. |  |
| `plugin_path` | **yes** | The folder where the source code is located. Shouldn't have any dash character. Defaults to: `slugify(plugin_name)`. | qgis_plugin_CI_testing |
| `project_slug` | no | The *project* slug on SCM host (e.g. Github) and translation platform (e.g. Transifex).<br/>Not required when running on Travis since deduced from `$TRAVIS_REPO_SLUG`environment variable. |  |

## Examples

### Using YAML file `.qgis-plugin-ci`

```yaml
plugin_path: qgis_plugin_ci_testing
github_organization_slug: opengisch
project_slug: qgis-plugin-ci
```

### Using INI file `setup.cfg`

```ini
[qgis-plugin-ci]
plugin_path = QuickOSM
github_organization_slug = 3liz
project_slug = QuickOSM
```
