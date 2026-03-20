#!/usr/bin/env bash
set -e
pip install --upgrade pip
pip install hatchling
pip install -r requirements.txt
pip install --no-deps .
