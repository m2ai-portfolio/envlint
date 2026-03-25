"""Usage checking for environment variables in source code."""

import re
import os
from pathlib import Path
from typing import Set, List, Tuple, Dict


# Python patterns for environment variable access
PYTHON_PATTERNS = [
    r"os\.getenv\(['\"]([A-Z_][A-Z0-9_]*?)['\"](?:\s*,\s*[^)]+)?\)",
    r"os\.environ\.get\(['\"]([A-Z_][A-Z0-9_]*?)['\"](?:\s*,\s*[^)]+)?\)",
    r"os\.environ\[['\"]([A-Z_][A-Z0-9_]*?)['\"]\]",
    r"environ\.get\(['\"]([A-Z_][A-Z0-9_]*?)['\"](?:\s*,\s*[^)]+)?\)",
    r"environ\[['\"]([A-Z_][A-Z0-9_]*?)['\"]\]",
]

# TypeScript/JavaScript patterns for environment variable access
TYPESCRIPT_PATTERNS = [
    r"process\.env\.([A-Z_][A-Z0-9_]*)",
    r"process\.env\[['\"]([A-Z_][A-Z0-9_]*?)['\"]\]",
]

# Default file extensions for scanning
DEFAULT_EXTENSIONS = {
    'python': ['.py'],
    'typescript': ['.ts', '.tsx', '.js', '.jsx']
}

# Maximum file size to scan (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


def scan_source_content(content: str, language: str = "python") -> Set[str]:
    """
    Scan source code content for environment variable usage.

    Args:
        content: Source code content as string
        language: Language type ("python" or "typescript")

    Returns:
        Set of environment variable names found
    """
    env_vars = set()

    # Select patterns based on language
    if language.lower() == "python":
        patterns = PYTHON_PATTERNS
    elif language.lower() in ["typescript", "javascript", "ts", "js"]:
        patterns = TYPESCRIPT_PATTERNS
    else:
        # Default to Python patterns
        patterns = PYTHON_PATTERNS

    # Search for all patterns
    for pattern in patterns:
        matches = re.findall(pattern, content)
        env_vars.update(matches)

    return env_vars


def scan_source_directory(directory: str, extensions: List[str] = None) -> Set[str]:
    """
    Recursively scan a directory for environment variable usage.

    Args:
        directory: Path to directory to scan
        extensions: List of file extensions to scan (e.g., ['.py', '.ts'])
                   If None, scans both Python and TypeScript files

    Returns:
        Set of environment variable names found

    Raises:
        ValueError: If directory doesn't exist
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        raise ValueError(f"Directory not found: {directory}")

    if not dir_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")

    # Use default extensions if none provided
    if extensions is None:
        extensions = DEFAULT_EXTENSIONS['python'] + DEFAULT_EXTENSIONS['typescript']

    env_vars = set()

    # Recursively scan all files with matching extensions
    for file_path in dir_path.rglob('*'):
        if file_path.is_file() and file_path.suffix in extensions:
            try:
                # Check file size before reading
                file_size = file_path.stat().st_size
                if file_size > MAX_FILE_SIZE:
                    # Skip files that are too large
                    print(f"Warning: Skipping large file {file_path} ({file_size / 1024 / 1024:.1f} MB)")
                    continue

                # Determine language from file extension
                if file_path.suffix in DEFAULT_EXTENSIONS['python']:
                    language = 'python'
                else:
                    language = 'typescript'

                # Read and scan file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    found_vars = scan_source_content(content, language)
                    env_vars.update(found_vars)
            except (UnicodeDecodeError, PermissionError):
                # Skip files that can't be read
                continue

    return env_vars


def check_usage(env_vars: Dict[str, str], used_vars: Set[str]) -> Tuple[List[str], List[str]]:
    """
    Check for missing and unused environment variables.

    Args:
        env_vars: Dictionary of environment variables from .env file
        used_vars: Set of environment variable names used in source code

    Returns:
        Tuple of (missing_in_env, unused_in_env)
        - missing_in_env: Variables used in code but not in .env
        - unused_in_env: Variables in .env but not used in code
    """
    env_keys = set(env_vars.keys())

    # Variables used in code but missing from .env
    missing_in_env = sorted(list(used_vars - env_keys))

    # Variables in .env but not used in code
    unused_in_env = sorted(list(env_keys - used_vars))

    return missing_in_env, unused_in_env
