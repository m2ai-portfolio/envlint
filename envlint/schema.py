"""Schema validation logic for .env files."""

import re
import json
import signal
import threading
from pathlib import Path
from typing import Dict, List, Optional
from .models import Schema, LintResult

# Constants for security
MAX_REGEX_PATTERN_LENGTH = 200
REGEX_TIMEOUT_SECONDS = 1


def parse_env_content(content: str) -> Dict[str, str]:
    """
    Parse .env file content into a dictionary.

    Handles:
    - key=value pairs
    - Comments (lines starting with #)
    - Blank lines
    - Quoted values (strips quotes)
    - Inline comments
    - Empty quoted values (KEY="")
    - Unmatched quotes (treated as error)

    Args:
        content: Content of .env file as string

    Returns:
        Dictionary of environment variables

    Raises:
        ValueError: If parsing fails or unmatched quotes found
    """
    env_vars = {}
    warnings = []

    for line_num, line in enumerate(content.split('\n'), 1):
        # Strip whitespace
        line = line.strip()

        # Skip blank lines and comments
        if not line or line.startswith('#'):
            continue

        # Check for lines without '='
        if '=' not in line:
            warnings.append(f"Line {line_num}: No '=' found, skipping: {line}")
            continue

        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip()

        # Handle quoted values
        if value.startswith('"') or value.startswith("'"):
            quote_char = value[0]
            end_quote = value.find(quote_char, 1)

            if end_quote == -1:
                # Unmatched quote
                raise ValueError(f"Line {line_num}: Unmatched quote in value for key '{key}'")

            # Extract quoted value (handles empty strings like KEY="")
            value = value[1:end_quote]
        else:
            # Unquoted value - split on first # for inline comment
            comment_pos = value.find('#')
            if comment_pos != -1:
                value = value[:comment_pos].strip()

        env_vars[key] = value

    return env_vars


def parse_env_file(env_path: str) -> Dict[str, str]:
    """
    Parse a .env file into a dictionary.

    Args:
        env_path: Path to .env file

    Returns:
        Dictionary of environment variables
    """
    try:
        with open(env_path, 'r') as f:
            content = f.read()
        return parse_env_content(content)
    except FileNotFoundError:
        raise FileNotFoundError(f"Env file not found: {env_path}")
    except Exception as e:
        raise ValueError(f"Error parsing env file: {e}")


def validate_regex_pattern(pattern: str, key: str) -> None:
    """
    Validate a regex pattern for security issues.

    Args:
        pattern: Regex pattern to validate
        key: Key name (for error messages)

    Raises:
        ValueError: If pattern is too long or invalid
    """
    if len(pattern) > MAX_REGEX_PATTERN_LENGTH:
        raise ValueError(
            f"Regex pattern for '{key}' exceeds maximum length of {MAX_REGEX_PATTERN_LENGTH} characters"
        )

    try:
        re.compile(pattern)
    except re.error as e:
        raise ValueError(f"Invalid regex pattern for '{key}': {e}")


def load_schema_from_dict(data: dict) -> Schema:
    """
    Load schema from dictionary.

    Args:
        data: Dictionary containing schema definition

    Returns:
        Schema object

    Raises:
        ValueError: If schema is invalid or contains unsafe patterns
    """
    pattern = data.get('pattern', {})

    # Validate all regex patterns during schema loading
    for key, regex_pattern in pattern.items():
        validate_regex_pattern(regex_pattern, key)

    return Schema(
        required=data.get('required', []),
        pattern=pattern,
        allowed=data.get('allowed', None)
    )


def load_schema(schema_path: str) -> Schema:
    """
    Load schema from JSON file.

    Args:
        schema_path: Path to schema JSON file

    Returns:
        Schema object
    """
    try:
        with open(schema_path, 'r') as f:
            data = json.load(f)

        return load_schema_from_dict(data)
    except FileNotFoundError:
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in schema file: {e}")
    except Exception as e:
        raise ValueError(f"Error loading schema: {e}")


class RegexTimeoutError(Exception):
    """Raised when regex matching times out."""
    pass


def _timeout_handler(signum, frame):
    """Handler for regex timeout."""
    raise RegexTimeoutError("Regex matching timed out")


def safe_regex_match(pattern: str, value: str, timeout: int = REGEX_TIMEOUT_SECONDS) -> Optional[bool]:
    """
    Perform regex matching with timeout protection.

    Args:
        pattern: Regex pattern to match
        value: Value to test
        timeout: Timeout in seconds

    Returns:
        True if matches, False if doesn't match, None if timeout/error

    Raises:
        RegexTimeoutError: If regex matching takes too long
    """
    try:
        # Use threading-based timeout for compatibility with Flask
        result_container = [None]
        exception_container = [None]

        def do_match():
            try:
                result_container[0] = re.match(pattern, value) is not None
            except Exception as e:
                exception_container[0] = e

        thread = threading.Thread(target=do_match, daemon=True)
        thread.start()
        thread.join(timeout=timeout)

        if thread.is_alive():
            # Thread is still running - timeout occurred
            raise RegexTimeoutError("Regex matching timed out")

        if exception_container[0]:
            raise exception_container[0]

        return result_container[0]

    except RegexTimeoutError:
        raise
    except Exception:
        return None


def validate_schema(env_vars: Dict[str, str], schema: Schema) -> List[str]:
    """
    Validate environment variables against schema.

    Checks:
    - All required keys are present
    - No keys outside allowed list (if allowed is specified)
    - Values match regex patterns where defined

    Args:
        env_vars: Dictionary of environment variables from .env
        schema: Schema to validate against

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check required keys
    for required_key in schema.required:
        if required_key not in env_vars:
            errors.append(f"Missing required key: {required_key}")

    # Check allowed keys
    if schema.allowed is not None:
        for key in env_vars.keys():
            if key not in schema.allowed:
                errors.append(f"Unknown key not in allowed list: {key}")

    # Check pattern matching with timeout protection
    for key, pattern in schema.pattern.items():
        if key in env_vars:
            value = env_vars[key]
            try:
                match_result = safe_regex_match(pattern, value)
                if match_result is False:
                    errors.append(
                        f"Value for '{key}' does not match pattern '{pattern}': {value}"
                    )
                elif match_result is None:
                    errors.append(f"Error validating pattern for '{key}'")
            except RegexTimeoutError:
                errors.append(f"Regex pattern for '{key}' timed out (possible ReDoS attack)")
            except Exception as e:
                errors.append(f"Error validating pattern for '{key}': {e}")

    return errors


def lint_env_file(env_path: str, schema_path: str) -> LintResult:
    """
    Main linting function for .env files.

    Args:
        env_path: Path to .env file
        schema_path: Path to schema JSON file

    Returns:
        LintResult with validation results
    """
    result = LintResult()

    try:
        # Parse .env file
        env_vars = parse_env_file(env_path)

        # Load schema
        schema = load_schema(schema_path)

        # Validate against schema
        result.schema_errors = validate_schema(env_vars, schema)

    except (FileNotFoundError, ValueError) as e:
        result.schema_errors.append(str(e))

    return result
