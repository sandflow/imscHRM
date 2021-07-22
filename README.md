# IMSC Hypothetical Render Model (HRM) Validator

     __  _  _  ____   ___  _  _  ____  _  _ 
    (  )( \/ )/ ___) / __)/ )( \(  _ \( \/ )
     )( / \/ \\___ \( (__ ) __ ( )   // \/ \
    (__)\_)(_/(____/ \___)\_)(_/(__\_)\_)(_/

## Introduction

_imschrm_ validates [IMSC](https://www.w3.org/TR/ttml-imsc1.1) documents against the [IMSC Hypothetical Render Model
(HRM)](https://www.w3.org/TR/ttml-imsc1.1/#hypothetical-render-model), which constrains document complexity.

_imschrm_ consists of a library and command line application written in pure Python, and uses
[ttconv](https://github.com/sandflow/ttconv).

## Known issues

Issues are tracked at https://github.com/sandflow/imscHRM/issues.

## Quick start

```sh
    pip install imschrm
    imschrm <input IMSC document>
```

## Command line

```sh
cli.py [-h] [--itype {ttml,manifest}] input
```

* `input`: input file
* `--itype`: specifies whether the input file is a single IMSC document (`ttml`) (default) or a manifest (`manifest`) containing a
  list of IMSC documents.

The manifest is a JSON file that conforms to the schema at `src/main/resources/json/manifest.json.schema`.

_EXAMPLE_:

```json
[
  {
    "begin": "12/24",
    "end": 1,
    "path": "doc001.ttml"
  },
  {
    "begin": 1,
    "end": null,
    "path": "doc002.ttml"
  }
]
```

## Dependencies

### General

The project uses [pipenv](https://pypi.org/project/pipenv/) to manage dependencies.

### Runtime

* [python >= 3.7](https://python.org)
* [ttconv == 1.0.1](https://github.com/sandflow/ttconv)

### Development

* [pylint](https://pypi.org/project/pylint/)

## Development environment

* run `pipenv install --dev`
* set the `PYTHONPATH` environment variable to `src/main/python`, e.g. `export PYTHONPATH=src/main/python`
* `pipenv run` can then be used

From the root directory of the project:

```sh
pipenv install --dev
mkdir build
export PYTHONPATH=src/main/python
pipenv run python src/main/python/imschrm/cli.py src/test/resources/ttml/fail001.ttml
```

