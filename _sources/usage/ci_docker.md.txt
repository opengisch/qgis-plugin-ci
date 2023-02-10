# Docker

3Liz is maintaining a small docker image of this package available on [GitHub](https://github.com/3liz/docker-qgis-plugin-ci)
and [Docker Hub](https://hub.docker.com/r/3liz/qgis-plugin-ci).

This is an example with GitLab-CI running with the Docker image from Docker Hub :

```yaml
package:
  stage: package
  only:
    - tags
  image: 3liz/qgis-plugin-ci:latest
  script:
    - >
      qgis-plugin-ci
      package ${CI_COMMIT_REF_NAME}
      --plugin-repo-url https://custom.server.url/
  artifacts:
    expose_as: 'QGIS package'
    paths:
      - ${PLUGIN_NAME}.${CI_COMMIT_REF_NAME}.zip
      - plugins.xml
```
