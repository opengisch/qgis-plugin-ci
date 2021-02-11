# Using Transifex to translate your plugin

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
