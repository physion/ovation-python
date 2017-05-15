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

### API tokens

If an API token exists in `~/.ovation/credentials.json`, `ovation.session.connect` will automatically use the correct token so you don't have to enter your password. Once a token is generated, you can save it to `credentials.json`. This file lists tokens by user (email) and host:

```
{
    "api.ovation.io": {
        "YOUR EMAIL": "YOUR TOKEN HERE"
    }
}
```

If you use both the Ovation Research and Lab APIs, you can enter tokens for both:

```
{
    "api.ovation.io": {
        "YOUR EMAIL": "YOUR RESEARCH TOKEN"
    },
    "lab-services.ovation.io": {
        "YOUR EMAIL": "YOUR LAB TOKEN"
    }
}
```

**Your API token is secret**. Anyone with your API token has full access to your Ovation account. Make sure that the permissions on `credentials.json` allow only you to access the file. On OS X or Linux, you can set the permissions like this:

	chmod go-rw ~/.ovation/credentials.json


### Listing projects from the terminal

You can list all of your Projects:

    python -m ovation.cli ls
    
### Listing project or folder contents from the terminal

You can list the contents of a `Project` or `Folder`:

    python -m ovation.cli ls <project or folder ID>

### Uploading files from the terminal

Use the `ovation.cli` module's `upload` command to upload files from your local file system to Ovation. Try

    python -m ovation.cli upload -h

for more info.

### Downloading files from the termainl

Use the `ovation.cli` module's `download` command to download a `Revision` from Ovation to your local file system. Try

    python -m ovation.cli download -h

for more info.

If you supply a `Project` or `Folder` ID as the download source, this command will recursively download the contents of the Project or Folder. **Be careful—this may download a lot of data**.

If you supply a `File` ID as the download source, this command will download the most recent version of the file.
