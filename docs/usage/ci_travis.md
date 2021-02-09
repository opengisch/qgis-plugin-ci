# Automatic deployment on Travis

## Basic configuration

**Notes**:

- Python 3.7 is required. Check on Travis that you are using at least Python 3.7.
- `qgis-plugin-ci` must find an existing GitHub release for the tag. Either you create the release from GitHub, which will trigger Travis or you can use Travis/GitHub Actions to create the release automatically.

One can easily set up a deployment using Travis.

1. Add `qgis-plugin-ci` to `requirements.txt` or have `pip install qgis-plugin-ci` in `install` step.
2. Specify the environment variables required to connect to the different platforms (Osgeo, Github, Transifex). You can add them either using the Travis CLI with `travis encrypt` or use the web interface to add the variables.
3. Add a deploy step to release the plugin:

```yaml
deploy:
  - provider: script
    script: qgis-plugin-ci release ${TRAVIS_TAG} --github-token ${GH_TOKEN} --osgeo-username ${OSGEO_USERNAME} --osgeo-password {OSGEO_PASSWORD}
    on:
      tags: true
```

This assumes that you have an existing GitHub release.
Alternatively, Travis can create the release by adding a `releases` provider before the `script` provider:

```yaml
- provider: releases
  name: Title of the release ${TRAVIS_TAG}
  api_key: ${GH_TOKEN}
  on:
    tags: true
```

## Submodules

If you have any submodule configured using ssh and not https, you need to change the connection url by doing:

```yaml
git:
  submodules: false

before_install:
  # cannot use SSH to fetch submodule
  - sed -i 's#git@github.com:#https://github.com/#' .gitmodules
  - git submodule update --init --recursive
```

When packaging the plugin, it's possible to not update the submodule using CLI options.

## Using Transifex to translate your plugin

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
