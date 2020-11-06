#!/usr/bin/env python3
# coding: utf-8
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
# -----------------------------------------------------------------------------
# Minimal Python version sanity check (from IPython and from JupyterHub)
# -----------------------------------------------------------------------------


import os
import shutil
import sys
from subprocess import check_call

from setuptools import setup
from setuptools.command.bdist_egg import bdist_egg


v = sys.version_info
if v[:2] < (3, 5):
    error = "ERROR: Tornado_ex requires Python version 3.5 or above."
    print(error, file=sys.stderr)
    sys.exit(1)

shell = False
if os.name in ('nt', 'dos'):
    shell = True
    warning = "WARNING: Windows is not officially supported"
    print(warning, file=sys.stderr)


pjoin = os.path.join

here = os.path.abspath(os.path.dirname(__file__))
#share_tornado_ex = pjoin(here, 'share', 'tornado_ex')


# ---------------------------------------------------------------------------
# Build basic package data, etc. (from JupyterHub)
# ---------------------------------------------------------------------------

# def get_data_files():
#     """Get data files in share/tornado_ex"""

#     data_files = []
#     ntrim = len(here + os.path.sep)

#     for (d, dirs, filenames) in os.walk(share_tornado_ex):
#         data_files.append((d[ntrim:], [pjoin(d, f) for f in filenames]))
#     return data_files


# ns = {}
# with open(pjoin(here, 'tornado_ex', '_version.py')) as f:
#     exec(f.read(), {}, ns)


packages = []
for d, _, _ in os.walk('tornado_ex'):
    if os.path.exists(pjoin(d, '__init__.py')):
        packages.append(d.replace(os.path.sep, '.'))

# with open('README.md', encoding="utf8") as f:
#     readme = f.read()

print(packages)

setup_args = dict(
    name='tornado_ex',
    packages=packages,
    #version=ns['__version__'],
    description="Tornado_ex: Tutorial for tornado",
    author="Gaelle Usseglio",
    author_email="gaelle.usseglio@thales-services.fr",
    license="BSD",
    platforms="Linux",
    keywords=['Interactive', 'Interpreter', 'Shell', 'Web'],
    python_requires=">=3.5",
    entry_points={
        'console_scripts': [
            'tornado_ex = tornado_ex.tornado_app:main'
        ],
    }
)

# setuptools requirements
setup_args['install_requires'] = install_requires = []

with open('requirements.txt') as f:
    for line in f.readlines():
        req = line.strip()
        if not req or req.startswith('#') or '://' in req:
            continue
        install_requires.append(req)

# ---------------------------------------------------------------------------
# setup
# ---------------------------------------------------------------------------

def main():
    setup(**setup_args)


if __name__ == '__main__':
    main()
