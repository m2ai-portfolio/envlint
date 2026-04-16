<p align="center">
  <img src="assets/infographic.png" alt="EnvLint" width="800">
</p>

<h3 align="center">CLI tool that validates .env files against a schema (required keys, format patterns, no secrets in git). Cross-references environment variables used in Python/TS source files to detect missing or unused vars.</h3>

<p align="center">
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#features">Features</a> &bull;
  <a href="#examples">Examples</a> &bull;
  <a href="#contributing">Contributing</a>
</p>

## What is this?
EnvLint is a command‑line utility that ensures your environment files are correct, complete, and safe. It reads a schema, checks your `.env` for required keys and forbidden patterns, scans your Python and TypeScript source files for variable usage, and reports any mismatches or secrets that may have been committed to Git.

```
$ envlint validate .env --schema schema.yaml
✅ .env file passes validation
🔍 Found 3 used vars in source: DB_HOST, DB_PORT, API_KEY
⚠️  Unused vars in .env: LOG_LEVEL
❌ Missing required var: SECRET_KEY
```

## Problem
Environment variable misconfigurations are a top cause of deployment failures and security incidents. Developers manually track which vars are needed, leading to missing keys in production and stale entries accumulating silently.

## Features
Feature | Description
--- | --- |
Schema validation | Ensures required keys exist, values match regex patterns, and no disallowed secrets appear in `.env`.
Git safety check | Scans commit history for accidentally committed secrets and blocks validation if any are found.
Source‑code cross‑reference | Parses Python and TypeScript files to collect actual env var usage and detect missing or unused entries.
Detailed reporting | Emits clear symbols and messages for passed checks, warnings, and failures, suitable for CI logs.
Web interface | Provides a lightweight HTML UI (via `web.py`) to visualise validation results locally.
Extensible output | Supports plain text, JSON, and HTML report formats for integration with different toolchains.

## Quick Start
1. Clone the repository:  
   `git clone https://github.com/m2ai-portfolio/EnvLint.git`
2. Enter the project directory:  
   `cd EnvLint`
3. Install the package in editable mode:  
   `pip install -e .`
4. Run a basic validation:  
   `envlint validate .env --schema schema.yaml`

## Examples
**Basic validation with default schema**  
```
$ envlint validate .env
✅ .env file passes validation
🔍 Found 2 used vars in source: API_ENDPOINT, CACHE_TTL
```
**Using a custom schema and ignoring Git checks**  
```
$ envlint validate .env --schema .envschema.yml --no-git-check
⚠️  Unused vars in .env: DEBUG_MODE, OLD_KEY
❌ Missing required var: ENCRYPTION_SALT
```
**Generating an HTML report via the web interface**  
```
$ envlint web --output report.html
🌐 Web UI available at http://localhost:8080
```
*(Opening the URL shows a table of validated vars, usage stats, and any issues.)*

## File Structure
```
EnvLint/
├── envlint/               # Core source code
│   ├── main.py            # CLI entry point (argparse based)
│   ├── schema.py          # Loads YAML/JSON schema, performs validation
│   ├── usage.py           # Scans .py and .ts files for env var references
│   ├── git.py             # Uses GitPython to detect committed secrets
│   ├── web.py             # Starts a Flask‑like server for the UI
│   ├── models.py          # Dataclasses for validation results
│   ├── templates/         # Jinja2 HTML templates for the web UI
│   └── __init__.py
├── assets/                # Static assets (infographic, etc.)
├── screenshots/           # Demo outputs and test logs
├── pyproject.toml         # Project metadata and dependencies
├── setup.py               # Legacy install script
├── init.sh                # Development environment setup helper
└── README.md
```

## Tech Stack
Technology | Purpose
--- | --- |
Python 3.8+ | Core language and runtime
Jinja2 | Rendering HTML templates for the web interface
PyYAML | Parsing schema files (YAML format)
GitPython | Accessing repository history to detect secrets
Standard Library (os, re, json, argparse) | File handling, regex parsing, CLI, data interchange

## Contributing
Fork the repository, make your changes, run the test suite, and submit a pull request.

## License
MIT

## Author
```
Matthew Snow -- [M2AI](https://m2ai.co) | [@m2ai-portfolio](https://github.com/m2ai-portfolio)