
import re
from setuptools import setup

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('etspi/cli.py').read(),
    re.M
    ).group(1)
assert version

with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")

setup(
    name = "etspi",
    packages = ["etspi"],
    entry_points = {
        "console_scripts": ['etspi = etspi.cli:cli']
        },
    version = version,
    description = "CLI App to manage Etsy shop and listings.",
    long_description = long_descr,
    author = "sov2000",
    author_email = "sv28k64@gmail.com",
    url = "https://github.com/sov2000/etspi-cli",
    keywords = ["etsy", "api", "shop", "manager"],
    platforms = ["POSIX", "Windows"],
    classifiers = [
        "Programming Language :: Python",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Other Audience",
        "Environment :: Console",
        ]
    )
