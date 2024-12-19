#!/usr/bin/env python

"""
$ python etspi-run.py 

$ python -m etspi.cli

Note: after installation with setuptools, a `etspi` command is available:
$ python setup.py install etspi

"""

from etspi.cli import cli

if __name__ == '__main__':
    cli()
