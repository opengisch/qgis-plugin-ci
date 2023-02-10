# Commands related to the translation

## Pull translations

```bash
usage: qgis-plugin-ci pull-translation [-h] [--compile] transifex_token

positional arguments:
  transifex_token  The Transifex API token

optional arguments:
  -h, --help       show this help message and exit
  --compile        Will compile TS files into QM files
```

## Push translations

```bash
usage: qgis-plugin-ci push-translation [-h] transifex_token

positional arguments:
  transifex_token  The Transifex API token

optional arguments:
  -h, --help       show this help message and exit
```
