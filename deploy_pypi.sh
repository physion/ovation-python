#!/usr/bin/env bash

FILE=~/.pypirc
echo > $FILE
echo "[distutils]" >> $FILE
echo "index-servers = pypi" >> $FILE
echo "[pypi]" >> $FILE
echo "username:$PYPI_USERNAME" >> $FILE
echo "password:$PYPI_PASSWORD" >> $FILE

python setup.py bdist upload
