"""Flask web interface for EnvLint (for testing purposes)."""

import json
from flask import Flask, render_template, request, jsonify
from .schema import parse_env_content, load_schema_from_dict, validate_schema
from .models import Schema
from .usage import scan_source_content, check_usage

app = Flask(__name__)


@app.route('/')
def index():
    """Serve the main validation form."""
    return render_template('index.html')


def sanitize_error_message(error_msg: str) -> str:
    """
    Sanitize error messages to prevent leaking internal paths.

    Args:
        error_msg: Original error message

    Returns:
        Sanitized error message
    """
    # Remove any file paths that might be in error messages
    import re
    # Remove Unix-style paths
    error_msg = re.sub(r'/[/\w\-\.]+', '[path]', error_msg)
    # Remove Windows-style paths
    error_msg = re.sub(r'[A-Za-z]:\\[\\\w\-\.]+', '[path]', error_msg)
    return error_msg


@app.route('/validate', methods=['POST'])
def validate():
    """
    Validate .env content against schema.

    Expects JSON with:
        - env_content: string content of .env file
        - schema_content: JSON string of schema
        - source_code: (optional) source code content to check usage
        - language: (optional) language of source code ("python" or "typescript")

    Returns JSON with:
        - success: boolean
        - errors: list of error messages
        - warnings: list of warning messages
        - usage_missing: list of variables used in code but not in .env
        - usage_unused: list of variables in .env but not used in code
    """
    try:
        data = request.get_json()
        env_content = data.get('env_content', '')
        schema_content = data.get('schema_content', '')
        source_code = data.get('source_code', '')
        language = data.get('language', 'python')

        # Validate language parameter
        VALID_LANGUAGES = ['python', 'typescript', 'javascript', 'ts', 'js']
        if language not in VALID_LANGUAGES:
            return jsonify({
                'success': False,
                'errors': [f'Invalid language parameter: {language}. Must be one of: {", ".join(VALID_LANGUAGES)}'],
                'warnings': [],
                'usage_missing': [],
                'usage_unused': []
            }), 400

        # Parse schema from JSON string
        try:
            schema_data = json.loads(schema_content)
        except json.JSONDecodeError as e:
            return jsonify({
                'success': False,
                'errors': [f'Invalid schema JSON: {str(e)}'],
                'warnings': [],
                'usage_missing': [],
                'usage_unused': []
            }), 400

        # Load schema and validate patterns
        schema = load_schema_from_dict(schema_data)

        # Parse env content
        env_vars = parse_env_content(env_content)

        # Validate schema
        errors = validate_schema(env_vars, schema)

        # Usage checking if source code provided
        usage_missing = []
        usage_unused = []

        if source_code.strip():
            # Scan source code for env var usage
            used_vars = scan_source_content(source_code, language)

            # Check for missing and unused variables
            usage_missing, usage_unused = check_usage(env_vars, used_vars)

            # Add missing vars to errors
            for var in usage_missing:
                errors.append(f"Variable used in code but missing from .env: {var}")

        # Sanitize error messages to prevent path leakage
        sanitized_errors = [sanitize_error_message(err) for err in errors]
        sanitized_warnings = [f"Unused variable in .env: {var}" for var in usage_unused]

        if sanitized_errors:
            return jsonify({
                'success': False,
                'errors': sanitized_errors,
                'warnings': sanitized_warnings,
                'usage_missing': usage_missing,
                'usage_unused': usage_unused
            })
        else:
            return jsonify({
                'success': True,
                'errors': [],
                'warnings': sanitized_warnings,
                'usage_missing': [],
                'usage_unused': usage_unused
            })

    except ValueError as e:
        # Sanitize error message
        error_msg = sanitize_error_message(str(e))
        return jsonify({
            'success': False,
            'errors': [f'Validation error: {error_msg}'],
            'warnings': [],
            'usage_missing': [],
            'usage_unused': []
        }), 400
    except Exception as e:
        # Sanitize error message
        error_msg = sanitize_error_message(str(e))
        return jsonify({
            'success': False,
            'errors': [f'Unexpected error: {error_msg}'],
            'warnings': [],
            'usage_missing': [],
            'usage_unused': []
        }), 500


def run_server(port=5000):
    """Run the Flask development server."""
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    run_server()
