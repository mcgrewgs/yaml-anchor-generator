#!/bin/bash

FILE_IN="${1:-sample_in.yml}"
FILE_OUT="${2:-sample_out.yml}"

make update
pipenv run python yaml_anchor_generator/dump.py -i "${FILE_IN}" "${FILE_OUT}"
