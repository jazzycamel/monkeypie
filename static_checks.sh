#!/usr/bin/env bash
poetry run ruff format
poetry run ruff check . --fix
poetry run mypy .