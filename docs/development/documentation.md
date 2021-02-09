# Documentation

Project uses Sphinx to generate documentation from docstrings (documentation in-code) and custom pages written in Markdown (througth the [MyST parser](https://myst-parser.readthedocs.io/en/latest/)).

## Build documentation website

To build it:

```bash
# install aditionnal dependencies
python -m pip install -U -r requirements/documentation.txt
# build it
sphinx-build -b html docs docs/_build/html
```

Open `docs/_build/index.html` in a web browser.

## Write documentation using live render

```bash
sphinx-autobuild -b html . ./_build
```

Open <http://localhost:8000> in a web browser to see the HTML render updated when a file is saved.

## Add a new page to the documentation

For example, to add a usage in a new language:

1. Create a markdown file into `docs/usage/usage_{locale}.md` where `{locale}` is the language code (en, fr, it, sp...)
2. Reference this new page in the homepage toctree:

````markdown
```{toctree}
---
caption: How to use the plugin
maxdepth: 1
---
usage/index
usage/usage_en
usage/usage_fr
```
````
