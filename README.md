# MonkeyPie
## Install
```bash
poetry install
```
## Tests
```bash
poetry run python -m unittest
```

## Static Checks
```bash
./static_checks.sh
```

This will run `ruff` to format and lint the code and then `mypy` to check for type errors.

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