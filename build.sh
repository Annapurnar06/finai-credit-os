#!/usr/bin/env bash
set -e
pip install --upgrade pip
pip install -r requirements-render.txt
pip install hatchling
pip install --no-deps .
