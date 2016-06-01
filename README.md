# Ovation Python API

[ ![Codeship Status for physion/ovation-python](https://codeship.com/projects/4349c120-e3e2-0133-8c41-5e6dd4ce3e38/status?branch=master)](https://codeship.com/projects/146183)

Ovation is the powerful data management service engineered specifically for scientists that liberates research through organization of multiple data formats and sources, the ability to link raw data with analysis and the freedom to safely share all of this with colleagues and collaborators.

The Ovation Python API wraps the Ovation Rest API. Through this Python API, CPython users can access the full functionality of the Ovation ecosystem from within Python. 


## Requirements

* Python 2.7+, 3.4+

## Installation

Install the `ovation` package from [PyPI](http://pypi.python.org):

	pip install ovation


## Usage

### Session

To create a session, connect using your Ovation user email and password:

    from ovation.session import connect

    my_session = connect('example@ovation.io')


You can supply your password as a `password=...` keyword parameter if you're using the Ovation API from a script. But for most cases, you'll want to let the Ovation API prompt you for your password (this works in the Python/IPython terminal or in a Jupyter notebook).


### Uploading files from the terminal

Use the `ovation.upload` module to upload files from your local file system to Ovation. Try

    python -m ovation.upload -h

for more info.

### Downloading files from the termainl

Use the `ovation.download` module to download a `Revision` from Ovation to your local file system. Try

    pythyon -m ovation.download -h

for more info.
