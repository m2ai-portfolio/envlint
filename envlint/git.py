"""Git tracking check for .env files."""

import subprocess
import os
from pathlib import Path
from typing import Dict


def validate_env_file_path(env_file: str) -> str:
    """
    Validate and sanitize env file path to prevent command injection.

    Args:
        env_file: Path to .env file

    Returns:
        Sanitized absolute path

    Raises:
        ValueError: If path contains suspicious characters
    """
    # Check for suspicious characters that could be used for command injection
    suspicious_chars = [';', '|', '&', '\n', '\r', '\0']
    for char in suspicious_chars:
        if char in env_file:
            raise ValueError(f"Invalid character in env_file path: {repr(char)}")

    # Canonicalize the path to prevent path traversal
    try:
        resolved_path = Path(env_file).resolve()
        return str(resolved_path)
    except Exception as e:
        raise ValueError(f"Invalid path: {env_file}")


def check_git_tracking(env_file: str = ".env") -> dict:
    """
    Check if .env file is tracked by git.

    Args:
        env_file: Path to .env file (default: ".env")

    Returns:
        Dictionary with:
            - is_git_repo: True if .git directory exists
            - is_tracked: True if .env is tracked by git
            - is_ignored: True if .env is in .gitignore
            - git_available: True if git command is available
            - message: Human-readable status message

    Raises:
        subprocess.TimeoutExpired: If git command times out
        subprocess.CalledProcessError: If git command fails unexpectedly
        ValueError: If env_file path is invalid or contains suspicious characters
    """
    # Validate env_file path to prevent command injection
    env_file = validate_env_file_path(env_file)

    result = {
        "is_git_repo": False,
        "is_tracked": False,
        "is_ignored": False,
        "git_available": False,
        "message": ""
    }

    # Check if git is available
    try:
        subprocess.run(
            ["git", "--version"],
            capture_output=True,
            timeout=5,
            check=True
        )
        result["git_available"] = True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        result["message"] = "Git command not available"
        return result

    # Check if current directory is a git repository
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            timeout=5,
            check=True,
            cwd=os.path.dirname(os.path.abspath(env_file)) or "."
        )
        result["is_git_repo"] = True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        result["message"] = "Not in a git repository"
        return result

    # Check if .env file is tracked by git
    # git ls-files --error-unmatch returns exit code 0 if file is tracked
    try:
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", env_file],
            capture_output=True,
            timeout=5,
            check=True,
            cwd=os.path.dirname(os.path.abspath(env_file)) or "."
        )
        result["is_tracked"] = True
        result["message"] = f"WARNING: {env_file} is tracked by git (security risk!)"
    except subprocess.CalledProcessError:
        # File is not tracked (good!)
        result["is_tracked"] = False
    except subprocess.TimeoutExpired:
        result["message"] = "Git command timed out"
        return result

    # Check if .env is in .gitignore
    # git check-ignore returns exit code 0 if file is ignored
    try:
        subprocess.run(
            ["git", "check-ignore", env_file],
            capture_output=True,
            timeout=5,
            check=True,
            cwd=os.path.dirname(os.path.abspath(env_file)) or "."
        )
        result["is_ignored"] = True
        if not result["is_tracked"]:
            result["message"] = f"{env_file} is properly ignored by git"
    except subprocess.CalledProcessError:
        # File is not ignored
        result["is_ignored"] = False
        if not result["is_tracked"]:
            result["message"] = f"{env_file} is not tracked (but also not in .gitignore)"
    except subprocess.TimeoutExpired:
        result["message"] = "Git command timed out"
        return result

    return result


def check_git_tracking_safe(env_file: str = ".env") -> dict:
    """
    Safe version of check_git_tracking that never throws exceptions.

    Wraps all subprocess calls in try/except to ensure it never crashes.
    Useful for web interface where we want graceful degradation.

    Args:
        env_file: Path to .env file (default: ".env")

    Returns:
        Dictionary with git tracking status (same as check_git_tracking)
    """
    try:
        return check_git_tracking(env_file)
    except Exception as e:
        # Sanitize error message to prevent information disclosure
        return {
            "is_git_repo": False,
            "is_tracked": False,
            "is_ignored": False,
            "git_available": False,
            "message": "Error checking git status"
        }
