#!/usr/bin/env python

import os

def is_conda():
    if 'CONDA_BUILD' in os.environ:
        return True

    return False

if is_conda():
    from distutils.core import setup
else:
    from setuptools import setup

DESCRIPTION =  """
Ovation is the powerful data management service engineered specifically for scientists that liberates research through organization of multiple data formats and sources, the ability to link raw data with analysis and the freedom to safely share all of this with colleagues and collaborators.

The Ovation Python API wraps the Ovation Java API for use by CPython. Through this Python API, CPython users can access the full functionality of the Ovation ecosystem from within Python. 

Jython users can access the Ovation Java API directly and should *not* use this Python API."""


VERSION = "2.1.8"

args = dict(name='ovation',
      version=VERSION,
      description='Ovation Python API',
      author='Physion LLC',
      author_email='info@ovation.io',
      url='http://ovation.io',
      long_description=DESCRIPTION,
      packages=['ovation', 'ovation.api', 'ovation.core', 'ovation.test', 'ovation.test.util'],
      package_data={'ovation' : ["jars/*.jar"]},
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
      ])


if not is_conda():
    args.update(zip_safe=False,
                setup_requires=['nose>=1.3.0', 'coverage==3.6', 'mock>=1.0.1'],
                install_requires=["phyjnius >= 1.2.1",
                                 "scipy >= 0.12.0",
                                 "pandas >= 0.11.0",
                                 "quantities >= 0.10.1",
                                 "requests >= 1.2.3",
                                 "progressbar >= 2.2"
                                 ],
                test_suite='nose.collector')

setup(**args)


