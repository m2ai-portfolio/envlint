"""CLI entry point for EnvLint."""

import sys
import click
from pathlib import Path
from .schema import lint_env_file, parse_env_file
from .models import LintResult
from .usage import scan_source_directory, check_usage
from .git import check_git_tracking


def print_result(result: LintResult) -> None:
    """
    Print lint results with colored output.

    Args:
        result: LintResult to print
    """
    # Print errors
    if result.schema_errors:
        click.secho("\n❌ Schema Validation Errors:", fg='red', bold=True)
        for error in result.schema_errors:
            click.secho(f"  • {error}", fg='red')

    # Print usage errors (missing vars)
    if result.usage_missing:
        click.secho("\n❌ Usage Errors:", fg='red', bold=True)
        for var in result.usage_missing:
            click.secho(f"  • Variable used in code but missing from .env: {var}", fg='red')

    # Print warnings (unused vars)
    if result.usage_unused:
        click.secho("\n⚠️  Warnings:", fg='yellow', bold=True)
        for warning in result.usage_unused:
            click.secho(f"  • Unused variable in .env: {warning}", fg='yellow')

    # Print git tracking error
    if result.git_tracked:
        click.secho("\n❌ Git Tracking Error:", fg='red', bold=True)
        click.secho("  • .env file is tracked by git (should be in .gitignore)", fg='red')

    # Print success if no errors
    if not result.has_errors and not result.has_warnings:
        click.secho("\n✅ All validations passed!", fg='green', bold=True)

    # Print summary
    error_count = len(result.schema_errors) + len(result.usage_missing)
    if result.git_tracked:
        error_count += 1
    warning_count = len(result.usage_unused)

    click.echo()
    if error_count > 0:
        click.secho(f"Total: {error_count} error(s), {warning_count} warning(s)",
                   fg='red', bold=True)
    elif warning_count > 0:
        click.secho(f"Total: {warning_count} warning(s)", fg='yellow', bold=True)


@click.command()
@click.option('--env-file',
              default='.env',
              help='Path to .env file (default: .env)',
              type=click.Path(exists=True))
@click.option('--schema',
              default='schema.json',
              help='Path to schema JSON file (default: schema.json)',
              type=click.Path(exists=True))
@click.option('--source-dir',
              multiple=True,
              help='Source directory to scan for env var usage (can be specified multiple times)',
              type=click.Path(exists=True))
@click.option('--no-git-check',
              is_flag=True,
              help='Skip git tracking check')
def main(env_file: str, schema: str, source_dir: tuple, no_git_check: bool) -> None:
    """
    EnvLint - Validate .env files against a schema.

    Checks for missing required keys, unknown keys, and pattern violations.
    Optionally scans source directories to find unused/missing environment variables.
    Checks if .env file is tracked by git (can be disabled with --no-git-check).
    """
    click.secho(f"\n🔍 EnvLint - Validating {env_file} against {schema}\n",
               fg='cyan', bold=True)

    # Run schema validation
    result = lint_env_file(env_file, schema)

    # Run git tracking check (unless disabled)
    if not no_git_check:
        try:
            git_status = check_git_tracking(env_file)

            # If git is available and we're in a git repo, check tracking status
            if git_status["is_git_repo"]:
                if git_status["is_tracked"]:
                    result.git_tracked = True
                    click.secho(f"\n⚠️  Git check: {git_status['message']}", fg='yellow')
                elif git_status["is_ignored"]:
                    click.secho(f"\n✅ Git check: {git_status['message']}", fg='green')
                else:
                    click.secho(f"\n💡 Git check: {git_status['message']}", fg='cyan')
            else:
                # Not in a git repo - just inform user
                click.secho(f"\n💡 Git check: {git_status['message']}", fg='cyan')
        except Exception as e:
            # Don't fail the entire lint if git check fails
            click.secho(f"\n⚠️  Git check failed: {e}", fg='yellow')

    # Run usage checking if source directories provided
    if source_dir:
        click.secho("📂 Scanning source directories for environment variable usage...\n",
                   fg='cyan')

        try:
            # Scan all provided source directories
            used_vars = set()
            for dir_path in source_dir:
                # Resolve path to handle symlinks and normalize
                real_path = Path(dir_path).resolve()
                click.echo(f"  Scanning: {real_path}")
                found_vars = scan_source_directory(str(real_path))
                used_vars.update(found_vars)

            click.echo(f"\n  Found {len(used_vars)} unique environment variable(s) in source code\n")

            # Parse env file to get current variables
            env_vars = parse_env_file(env_file)

            # Check for missing and unused variables
            missing, unused = check_usage(env_vars, used_vars)

            # Update result
            result.usage_missing = missing
            result.usage_unused = unused

        except ValueError as e:
            click.secho(f"\n❌ Error during usage checking: {e}", fg='red')
            sys.exit(1)

    # Print results
    print_result(result)

    # Exit with appropriate code
    sys.exit(1 if result.has_errors else 0)


if __name__ == '__main__':
    main()
