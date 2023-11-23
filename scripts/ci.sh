#!/bin/sh

# Exit immediately if unit tests exit with a non-zero status.
set -e

pipenv run python -m pylint --exit-zero src/main/python/imschrm/ src/test/python/
pipenv run python -m unittest discover -s src/test/python/