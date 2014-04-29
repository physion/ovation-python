# Ovation Python API


Ovation is the powerful data management service engineered specifically for scientists that liberates research through organization of multiple data formats and sources, the ability to link raw data with analysis and the freedom to safely share all of this with colleagues and collaborators.

The Ovation Python API wraps the Ovation Java API for use by CPython. Through this Python API, CPython users can access the full functionality of the Ovation ecosystem from within Python. 

Jython users can access the Ovation Java API directly and should *not* use this Python API.


## Requirements

* Java 1.6+
* CPython 2.7+ or 3.3+
* NumPy 1.7+
* Quantities 0.10+

## Installation

Install the `ovation` package from [PyPI](http://pypi.python.org):

	pip install ovation


### Windows

VS2008 Runtime: http://www.microsoft.com/en-us/download/details.aspx?id=29

Install Cython, NumPy, Scipy binaries from http://www.lfd.uci.edu/~gohlke/pythonlibs/#cython


Add to Path:

	C:\Program Files\Java\[jre7]\bin\client
	C:\Program Files\Java\[jre7]\bin\client

### OS X

Install the `ovation` package from [PyPI](http://pypi.python.org):

	pip install ovation
	
Note: if you are using Ovation from a Python virtualenv, see the [wiki](https://github.com/physion/ovation-python/wiki/Osx-virtualenv)

## Usage


### Connecting to the Ovation database

	>> from ovation.connection import new_data_context
	>> from ovation.conversion import to_list
	>> context = new_data_context(<ovation.io user email>)
	Ovation password: <ovation.io password>
	>> projects = to_list(context.getProjects())
	




