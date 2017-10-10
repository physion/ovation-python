#!/usr/bin/env bash

python setup.py sdist
twine -u $PYPI_USERNAME -p $PYPI_PASSWORD upload dist/*
