#!/usr/bin/env bash

python setup.py sdist
twine upload -u $PYPI_USERNAME -p $PYPI_PASSWORD dist/*
