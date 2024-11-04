#!/usr/bin/env python

"""
Convenience wrapper for testing development version of timegaps CLI without
installing. With the root directory of this repository as CWD, timegaps can be
invoked via

$ python etspi-run.py 


The canonical way would be (http://stackoverflow.com/a/3617928/145400):

$ python -m etspi.cli


Note: after installation with setuptools, a `timegaps` command is available:

$ python setup.py install etspi

"""

from etspi.cli import cli

if __name__ == '__main__':
    cli()
