"""CLI entry point for EnvLint."""

import sys
import click
from pathlib import Path
from .schema import lint_env_file
from .models import LintResult


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

    # Print warnings
    if result.usage_unused:
        click.secho("\n⚠️  Warnings:", fg='yellow', bold=True)
        for warning in result.usage_unused:
            click.secho(f"  • Unused variable: {warning}", fg='yellow')

    # Print git tracking warning
    if result.git_tracked:
        click.secho("\n⚠️  Git Warning:", fg='yellow', bold=True)
        click.secho("  • .env file is tracked by git (should be in .gitignore)", fg='yellow')

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
def main(env_file: str, schema: str) -> None:
    """
    EnvLint - Validate .env files against a schema.

    Checks for missing required keys, unknown keys, and pattern violations.
    """
    click.secho(f"\n🔍 EnvLint - Validating {env_file} against {schema}\n",
               fg='cyan', bold=True)

    # Run validation
    result = lint_env_file(env_file, schema)

    # Print results
    print_result(result)

    # Exit with appropriate code
    sys.exit(1 if result.has_errors else 0)


if __name__ == '__main__':
    main()
