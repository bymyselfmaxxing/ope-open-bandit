"""Makefile for the OPE study: setup, data, test, lint, check."""

PYTHON ?= python3

setup:
	$(PYTHON) -m pip install -e ".[dev]"

data:
	$(PYTHON) experiments/download_data.py

test:
	$(PYTHON) -m pytest --cov=src --cov-report=term-missing

lint:
	ruff check .

check: lint test

smoke:
	$(PYTHON) experiments/run_real_data.py --behavior-log tests/fixtures/bts_men_2k.csv --target-log tests/fixtures/random_men_2k.csv --n 200 --b 20
