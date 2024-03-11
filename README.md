# MonkeyPie
## Install
```bash
poetry install
```
## Tests
```bash
poetry run python -m unittest
```

To get a coverage report, run:
```bash
poetry run coverage run -m unittest
poetry run coverage report
```

## Static Checks
```bash
./static_checks.sh
```

This will run `ruff` to format and lint the code, `mypy` to check for type errors, `unittest` to run the tests
and `coverage` to check the test coverage.

## Run the REPL
```bash
poetry run python run repl.py
```

## Build Executable
```bash
poetry run pyinstaller monkey.spec
```

This will create a `dist` directory with the executable named `monkey` which can be run from the command line like so:
```bash
./dist/monkey
```