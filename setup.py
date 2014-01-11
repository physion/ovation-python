#!/usr/bin/env python

from setuptools import setup, find_packages

from dependencies import copy_dependencies

DESCRIPTION =  """
Ovation is the powerful data management service engineered specifically for scientists that liberates research through organization of multiple data formats and sources, the ability to link raw data with analysis and the freedom to safely share all of this with colleagues and collaborators.

The Ovation Python API wraps the Ovation Java API for use by CPython. Through this Python API, CPython users can access the full functionality of the Ovation ecosystem from within Python. 

Jython users can access the Ovation Java API directly and should *not* use this Python API."""
    
VERSION = "2.1.5"

JARS = "ovation/jars"

copy_dependencies(dest=JARS)

setup(name='ovation',
      version=VERSION,
      description='Ovation Python API',
      author='Physion LLC',
      author_email='info@ovation.io',
      url='http://ovation.io',
      long_description=DESCRIPTION,
      packages=find_packages(exclude=["test.*", "ez_setup", "examples"]),
      package_data={'ovation' : ["jars/*.jar"]},
      zip_safe=False,
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
      ],
      setup_requires=['nose>=1.3.0', 'coverage==3.6'],
      install_requires=["phyjnius >= 1.2.1",
                        "scipy >= 0.12.0",
                        "pandas >= 0.11.0",
                        "quantities >= 0.10.1",
                        ],
      test_suite='nose.collector',
)
