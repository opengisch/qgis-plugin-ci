# Configuration

## Settings

The plugin must have a configuration, located at the top directory; it can be either:

- a YAML file named `.qgis-plugin-ci`
- an INI file named `setup.cfg` with a `[qgis-plugin-ci]` section
- a TOML file (= your actual `pyproject.toml` file) with a `[tool.qgis-plugin-ci]` section.

In the configuration, you should at least provide the following configuration:

- `plugin_path`, the folder where the source code is located under the git repository. See

You can find a template `.qgis-plugin-ci` in this repository.
You can read the docstring of the [Parameters module](../_apidoc/qgispluginci.parameters)
to know parameters which are available in the file.

## Conventions

QGIS-Plugin-CI is best served if you use these two conventions:

- [Semantic versioning](https://semver.org/)
- [Keep A Changelog](https://keepachangelog.com)

## Options

| Name | Required | Description | Example |
| :--- | :------: | :---------- | :------ |
| `auto_approve` | no | Whether to request auto-approval after the server security scan when uploading via `--qgis-token` (token uploads only; only takes effect if the token owner has approval rights on plugins.qgis.org). Equivalent to and can be overridden by the `--auto-approve`/`--no-auto-approve` CLI option. Defaults to `true`. | `false` |
| `create_date` | no | Plugin creation date. Used as `create_date` attribute in the custom `plugins.xml` repository. Defaults to build timestamp. | `1985-07-21` |
| `github_organization_slug` | no | The *organization* slug on SCM host (e.g. Github) and translation platform (e.g. Transifex).<br/>Not required when running on Travis since deduced from `$TRAVIS_REPO_SLUG`environment variable. | `qgis` |
| `plugin_path` | **yes** | The folder where the source code is located. Shouldn't have any dash character. Defaults to: `slugify(plugin_name)`. | qgis_plugin_CI_testing |
| `project_slug` | no | The *project* slug on SCM host (e.g. Github) and translation platform (e.g. Transifex).<br/>Not required when running on Travis since deduced from `$TRAVIS_REPO_SLUG`environment variable. | `qgis-plugin-ci` |
| `repository_plugin_id` | no | The plugin identifier in the repository where it is published or is intended to be published. | Typically the same `plugin_id` value than on the official repository, i.e. `"3951"`. Or using a DNS prefix: `plugins.myorg.com:99999` |
| `repository_plugin_url` | no | Base URL for the custom plugins repository. Equivalent to and can be overridden by the `-u`/`--plugin-repo-url` CLI option. Typically, the GitHub/GitLab Pages base URL of your project. | `https://qgis.github.io/qgis-plugin-ci/` for this project. `https://oslandia.gitlab.io/qgis/oslandia/` for this plugin hosted on public GitLab instance. |
| `repository_url_raw` | no | Base URL to the source code repository. | `https://raw.githubusercontent.com/qgis/qgis-plugin-ci` for a plugin hosted on Github; `https://gitlab.com/Oslandia/qgis/oslandia/-/raw/` for a plugin hosted on gitlab. |
| `timezone` | no | The timezone for the plugin creation date. Defaults to: `UTC`. | `Europe/Paris` |

----

## Examples

### Using YAML file `.qgis-plugin-ci`

```yaml
plugin_path: qgis_plugin_ci_testing
github_organization_slug: qgis
project_slug: qgis-plugin-ci
```

### Using INI file `setup.cfg`

```ini
[qgis-plugin-ci]
plugin_path = QuickOSM
github_organization_slug = 3liz
project_slug = QuickOSM
```

### Using TOML file `pyproject.toml`

```toml
[tool.qgis-plugin-ci]
plugin_path = "qgis_plugin_ci_testing"
github_organization_slug = "qgis"
project_slug = "qgis-plugin-ci"
```
