# EnvLint

A Python CLI tool that validates .env files against a schema, cross-references environment variable usage in Python/TypeScript source code, and checks that .env isn't tracked by git.

## Features

- **Schema Validation**: Validate .env files against a defined schema to ensure required variables are present with correct types
- **Usage Checking**: Cross-reference environment variables in Python and TypeScript source code to detect unused or missing env vars
- **Git Ignore Check**: Verify that .env files are properly ignored by git and not accidentally tracked

## Quick Start

### Installation

```bash
pip install -e .
```

### Setup Development Environment

```bash
./init.sh
```

Then run:

```bash
envlint --help
```

## Usage Examples

### Validate .env file against schema

```bash
envlint validate --schema schema.yaml --env .env
```

### Check environment variable usage in source code

```bash
envlint check-usage --env .env --source src/
```

### Verify .env is in .gitignore

```bash
envlint check-gitignore --env .env
```

### Run all checks

```bash
envlint lint
```

## Tech Stack

- **Python**: 3.11+
- **CLI Framework**: Click
- **Schema Validation**: jsonschema / pydantic

## Project Structure

```
envlint/
├── README.md                 # This file
├── init.sh                   # Development setup script
├── .gitignore               # Git ignore rules
├── pyproject.toml           # Project configuration
├── requirements.txt         # Python dependencies
└── src/
    └── envlint/
        ├── __init__.py
        ├── cli.py           # Main CLI entry point
        ├── validator.py     # Schema validation logic
        ├── checker.py       # Usage checking logic
        └── git_check.py     # Git ignore verification
```

## Development

After running `./init.sh`, the virtual environment will be activated and dependencies installed.

To run tests:
```bash
pytest
```

To check code quality:
```bash
flake8 src/
mypy src/
```

## License

MIT
