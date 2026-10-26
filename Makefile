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
