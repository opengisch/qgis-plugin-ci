# Tests

## System requirements

```bash
sudo apt-get update
sudo apt-get install qt5-default qttools5-dev-tools
```

## Environment variables

```bash
export github_token={CHANGE_WITH_A_REAL_GITHUB_TOKEN}
export transifex_token={CHANGE_WITH_A_REAL_TRANSIFEX_TOKEN}
```

## Run tests

Run all tests:

```bash
nose2 -v
```

Run a specific test:

```bash
python -m unittest test.test_changelog
```
