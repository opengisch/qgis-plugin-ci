# QGIS Plugin CI

Contains scripts to perform automated testing and deployment for QGIS plugins.
These scripts are written for and tested on GitHub, Travis-CI and Transifex.

 - Deploy plugin releases on QGIS official plugin repository
 - Publish plugin in Github releases, option to deploy a custom repository
 - Easily integrated in Travis-CI
 - Completely handle translations with Transifex:
    - create the project and the languages
    - pull and push translations
    - all TS/QM files can be managed on the CI, the `i18n` folder can be omitted from the Git repository
   
# Command line

## Package

```commandline
usage: qgis-plugin-ci package [-h] [--transifex-token TRANSIFEX_TOKEN]
                              [--allow-uncommitted-changes]
                              release_version

positional arguments:
  release_version       The version to be released

optional arguments:
  -h, --help            show this help message and exit
  --transifex-token TRANSIFEX_TOKEN
                        The Transifex API token. If specified translations
                        will be pulled and compiled.
  --allow-uncommitted-changes
                        If False, uncommitted changes are not allowed before
                        packaging. If True and some changes are detected, a
                        hard reset on a stash create will be used to revert
                        changes made by qgis-plugin-ci.
```

## Release

```commandline
usage: qgis-plugin-ci release [-h] [--transifex-token TRANSIFEX_TOKEN]
                              [--github-token GITHUB_TOKEN]
                              [--create-plugin-repo]
                              [--osgeo-username OSGEO_USERNAME]
                              [--osgeo-password OSGEO_PASSWORD]
                              release_version

positional arguments:
  release_version       The version to be released

optional arguments:
  -h, --help            show this help message and exit
  --transifex-token TRANSIFEX_TOKEN
                        The Transifex API token. If specified translations
                        will be pulled and compiled.
  --github-token GITHUB_TOKEN
                        The Github API token. If specified, the archive will
                        be pushed to an already existing release.
  --create-plugin-repo  Will create a XML repo as a Github release asset.
                        Github token is required.
  --osgeo-username OSGEO_USERNAME
                        The Osgeo user name to publish the plugin.
  --osgeo-password OSGEO_PASSWORD
                        The Osgeo password to publish the plugin.
```

## Pull translations

```commandline
usage: qgis-plugin-ci pull-translation [-h] [--compile] transifex_token

positional arguments:
  transifex_token  The Transifex API token

optional arguments:
  -h, --help       show this help message and exit
  --compile        Will compile TS files into QM files
```

## Push translations

```commandline
usage: qgis-plugin-ci push-translation [-h] transifex_token

positional arguments:
  transifex_token  The Transifex API token

optional arguments:
  -h, --help       show this help message and exit
```

## Requirements

* The code is under a __git__ repository (`git archive` is used to bundle the plugin)
* There is no uncommitted changes when doing a package/release (there is an option to allow this)
* A `.qgis-plugin-ci` file contains the configuration at the top directory
* The source files of the plugin are within a sub-directory (possibly could work at top level, but not tested)

## The configuration file

In `.qgis-plugin-ci`, you should at least provide the following configuration:

* plugin_path

You can find a template `.qgis-plugin-ci` in this repository.
You can read the docstring of the file `qgispluginci/parameters.py`
to know parameters which are available in the file.

## QRC and UI files

- Any .qrc file in the source top directory (plugin_path) will be compiled and output as filename_rc.py. You can then import it using ``import plugin_path.resources_rc``
- Currently, qgis-plugin-ci does not compile any .ui file.

## Publishing plugins

When releasing, you can publish the plugin :

1. In the official QGIS plugin repository. You need to provide user name and password for your Osgeo account.
2. As a custom repository in Github releases and which can be added later in QGIS. The address will be: https://github.com/__ORG__/__REPO__/releases/latest/download/plugins.xml

Both can be achieved in the same process.
In the case of a pre-release, the plugin will not be pushed to the OSGEO repo. In such way, you can use the custom repo as beta testing and the OSGEO for the final rollout. 


## Automatic deployment on Travis

### Basic configuration

**Notes**:
* Python 3.7 is required. Check on Travis that you are using at least Python 3.7.
* `qgis-plugin-ci` must find an existing GitHub release for the tag. Either you create the release from GitHub, which will trigger Travis or you can use Travis/GitHub Actions to create the release automatically.

One can easily set up a deployment using Travis.

1. Add `qgis-plugin-ci` to `requirements.txt` or have `pip install qgis-plugin-ci` in `install` step.
2. Specify the environment variables required to connect to the different platforms (Osgeo, Github, Transifex). You can add them either using the Travis CLI with `travis encrypt` or use the web interface to add the variables.
3. Add a deploy step to release the plugin:

```
deploy:

  - provider: script
    script: qgis-plugin-ci release ${TRAVIS_TAG} --github-token ${GH_TOKEN} --osgeo-username ${OSGEO_USERNAME} --osgeo-password {OSGEO_PASSWORD}
    on:
      tags: true
```

This assumes that you have an existing GitHub release. 
Alternatively, Travis can create the release by adding a `releases` provider before the `script` provider:

```

  - provider: releases
    name: Title of the release ${TRAVIS_TAG}
    api_key: ${GH_TOKEN}
    on:
      tags: true

```


### Submodules

If you have any submodule configured using ssh and not https, you need to change the connection url by doing:

````yaml
git:
  submodules: false

before_install:
  # cannot use SSH to fetch submodule
  - sed -i 's#git@github.com:#https://github.com/#' .gitmodules
  - git submodule update --init --recursive
````

### Using Transifex to translate your plugin

```yaml
jobs:
  include:
    - stage: push-translation
      if: branch = master
      script: qgis-plugin-ci push-translation ${TX_TOKEN}

    - stage: deploy
      if: tag IS present
      script:
        - >
          qgis-plugin-ci release ${TRAVIS_TAG}
          --transifex-token ${TX_TOKEN}
          --github-token ${GH_TOKEN}
          --osgeo-username ${OSGEO_USERNAME}
          --osgeo-password ${OSGEO_PASSWORD}

```


## Debug

In any Python module, you can have a global variable as `DEBUG = True`, which will be changed to `False` when packaging the plugin.

## Excluding files in the plugin archive

If you want to avoid some files to be shipped with your plugin, create a ``.gitattributes`` file in which you can specify the files to ignore. For instance:
```
resources.qrc export-ignore
```

# Sample plugins

* https://github.com/opengisch/qgis_geomapfish_locator (translated, released on official repo)
* https://github.com/VeriVD/qgis_VeriVD (released on custom repo as Github release)
* https://github.com/3liz/lizmap-plugin (release on official repository, release created from Travis)
