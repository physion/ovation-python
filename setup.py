#!/usr/bin/env python

import os

def is_conda():
    return 'CONDA_BUILD' in os.environ

if is_conda():
    from distutils.core import setup
else:
    from setuptools import setup

DESCRIPTION =  """
Ovation is the powerful data management service engineered specifically for scientists that liberates research through organization of multiple data formats and sources, the ability to link raw data with analysis and the freedom to safely share all of this with colleagues and collaborators.

The Ovation Python API wraps the Ovation Rest API. Through this Python API, Python users can access the full functionality of the Ovation ecosystem.
"""


with open(os.path.join('ovation', '__init__.py')) as fd:
    versionline = [x for x in fd.readlines() if x.startswith('__version__')]
    version = versionline[0].split("'")[-2]


args = dict(name='ovation',
            version=version,
            description='Ovation Python API',
            author='Physion LLC',
            author_email='info@ovation.io',
            url='https://ovation.io',
            long_description=DESCRIPTION,
            packages=['ovation'],
            classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
      ])


if not is_conda():
    args.update(zip_safe=False,
                setup_requires=['nose>=1.3.7', 'coverage>=4.0.3'],
                install_requires=["requests >= 2.9.1",
                                  "six >= 1.10.0",
                                  "boto3 >= 1.3.0",
                                  ],
                test_suite='nose.collector')

setup(**args)


