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
EnvLint is a command‑line utility that helps developers keep their environment configuration in sync with their code. It checks a `.env` file against a user‑defined schema, ensures no secrets are committed to git, and scans Python/TypeScript source files to report missing or unused variables.

```
$ envlint check .env --schema schema.yml
✔ Schema validation passed
✔ No secrets found in git history
⚠ Unused var: DEBUG_MODE (declared in .env but not referenced in code)
✖ Missing var: API_KEY (referenced in src/main.py but absent from .env)
```

## Problem
Environment variable misconfigurations are a top cause of deployment failures and security incidents. Developers manually track which vars are needed, leading to missing keys in production and stale entries accumulating silently.

## Features
| Feature | Description |
|---------|-------------|
| Schema validation | Loads a YAML/JSON schema to enforce required keys and regex patterns on `.env` values. |
| Secret detection | Scans the git repository for accidental commits of credentials and fails if any are found. |
| Source‑code cross‑reference | Parses Python and TypeScript files to collect env var usage and reports mismatches. |
| Git integration | Uses `git.py` to safely inspect the repo without modifying it. |
| Web dashboard | Optional `web.py` server with `templates/index.html` provides a visual report of validation results. |
| Configurable ignoring | Allows listing of env vars to skip via `--ignore` flag or `.envlintignore` file. |
| Exit‑code reporting | Returns non‑zero status on validation failures for CI pipeline integration. |
| Extensible plugin system | New validators can be added by implementing the `Validator` interface in `models.py`. |

## Quick Start
1. Clone the repository:  
   ```bash
   git clone https://github.com/m2ai-portfolio/envlint.git
   cd envlint
   ```
2. Install the package in editable mode:  
   ```bash
   pip install -e .
   ```
3. Run a basic validation against a sample schema:  
   ```bash
   envlint check .env --schema schema.yml
   ```

## Examples
### Validate a project with a strict schema
**Command**  
```bash
envlint check .env --schema schema.yml --strict
```
**Sample output**  
```
✔ Required var DATABASE_URL present and matches pattern ^postgres://.+
✖ Invalid var LOG_LEVEL value "debuggy" does not match pattern ^(debug|info|warn|error)$
✔ No secrets detected in git
⚠ Unused var: TEMP_DIR
```

### Ignore specific variables and run in CI
**Command**  
```bash
envlint check .env --schema schema.yml --ignore DEBUG_MODE,TEMP_DIR
```
**Sample output**  
```
✔ Schema validation passed
✔ No secrets found in git history
✔ All used vars have corresponding entries
```

### Launch the web dashboard for interactive review
**Command**  
```bash
envlint web --port 8080
```
**Sample output**  
```
* Serving Flask app "envlint.web"
* Debug mode: off
* Running on http://127.0.0.1:8080/ (Press CTRL+C to quit)
```

## File Structure
```
EnvLint/
├── envlint/                  # Core source code
│   ├── main.py               # CLI entry point (argparse based)
│   ├── schema.py             # Schema loading and validation logic
│   ├── git.py                # Git helper functions for secret detection
│   ├── usage.py              # Parses Python/TS files for env var usage
│   ├── web.py                # Optional Flask web server
│   └── templates/            # HTML templates for the web UI
├── screenshots/              # Demo images and test artefacts
├── pyproject.toml            # Project metadata and dependencies
├── setup.py                  # Legacy install script
├── README.md
└── .gitignore
```

## Tech Stack
| Technology | Purpose |
|------------|---------|
| Python 3.8+ | Core language and runtime |
| Click | Command‑line interface framework |
| Jinja2 | Templating engine for the web dashboard |
| GitPython | Programmatic access to git repositories |
| PyYAML | Schema file parsing (YAML/JSON) |

## Contributing
- Fork the repository.
- Make your changes and run the test suite.
- Submit a pull request with a clear description.

## License
MIT

## Author
```
Matthew Snow -- [M2AI](https://m2ai.co) | [@m2ai-portfolio](https://github.com/m2ai-portfolio)