#! python3  # noqa: E265

# ############################################################################
# ########## Libraries #############
# ##################################

# standard library
import os
import pathlib
import sys

# 3rd party
from setuptools import setup

# package (to get version)
from qgispluginci import __about__

# ############################################################################
# ########## Globals #############
# ################################

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
python_min_version = (3, 7)

if os.getenv("CI") == "true":
    # Version is set by the CI with a tag
    VERSION = "__VERSION__"
else:
    # When using pip install -e /local/path/to/this/repo
    VERSION = "0.0.0"

# ############################################################################
# ########## Setup #############
# ##############################


if sys.version_info < python_min_version:
    sys.exit(
        "qgis-plugin-ci requires at least Python version {vmaj}.{vmin}.\n"
        "You are currently running this installation with\n\n{curver}".format(
            vmaj=python_min_version[0], vmin=python_min_version[1], curver=sys.version
        )
    )

setup(
    name="qgis-plugin-ci",
    author=__about__.__author__,
    author_email=__about__.__email__,
    description=__about__.__summary__,
    packages=["qgispluginci", "scripts"],
    long_description=README,
    long_description_content_type="text/markdown",
    entry_points={"console_scripts": ["qgis-plugin-ci = scripts.qgis_plugin_ci:main"]},
    package_data={"qgispluginci": ["plugins.xml.template"]},
    version=VERSION,
    url=__about__.__uri__,
    project_urls={
        "Docs": "https://opengisch.github.io/qgis-plugin-ci/",
        "Bug Reports": "{}issues/".format(__about__.__uri__),
        "Source": __about__.__uri__,
    },
    download_url="https://github.com/opengisch/qgis-plugin-ci/archive/{}.tar.gz".format(
        VERSION
    ),
    install_requires=[
        "GitPython>=3.1,<3.2",
        "PyGithub>=1.54,<1.56",
        "PyQt5>=5.15,<5.16",
        "pyqt5ac>=1.2,<1.3",
        "python-slugify>=4.0,<4.1",
        "pytransifex>=0.1.10,<0.2",
        "pyyaml>=5.4,<5.5",
    ],
    extras_require={
        "dev": ["black", "flake8", "pre-commit"],
    },
    python_requires=">={vmaj}.{vmin}".format(
        vmaj=python_min_version[0], vmin=python_min_version[1]
    ),
    # metadata
    keywords=["QGIS", "CI", "changelog", "plugin"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering :: GIS",
    ],
)
