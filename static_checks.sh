#!/usr/bin/env bash
printf "ruff\n====\n\n"
printf "format\n~~~~~~\n\n"
poetry run ruff format
printf "\ncheck\n~~~~~\n"
poetry run ruff check . --fix

printf "\nmypy\n====\n\n"
poetry run mypy .

printf "\nunittest\n========\n\n"
poetry run coverage run -m unittest

printf "\ncoverage\n========\n\n"
poetry run coverage report
