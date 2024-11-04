
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
    description = "Command line app to interact with Etsy V3 API for shop management.",
    long_description = long_descr,
    author = "Stas Ovcharenko",
    author_email = "stasovcharenko@gmail.com",
    url = "https://github.com/sov2000/etspi-cli",
    keywords = ["etsy", "api", "shop", "manager"],
    platforms = ["POSIX", "Windows"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: Beta",
        "License :: MIT License",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        ]
    )
