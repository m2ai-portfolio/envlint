"""Flask web interface for EnvLint (for testing purposes)."""

import json
from flask import Flask, render_template, request, jsonify
from .schema import parse_env_content, load_schema_from_dict, validate_schema
from .models import Schema
from .usage import scan_source_content, check_usage
from .git import check_git_tracking_safe

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
        - check_git: (optional) boolean to enable git tracking check

    Returns JSON with:
        - success: boolean
        - errors: list of error messages
        - warnings: list of warning messages
        - usage_missing: list of variables used in code but not in .env
        - usage_unused: list of variables in .env but not used in code
        - git_status: (optional) git tracking information
    """
    try:
        data = request.get_json()
        env_content = data.get('env_content', '')
        schema_content = data.get('schema_content', '')
        source_code = data.get('source_code', '')
        language = data.get('language', 'python')
        check_git = data.get('check_git', False)

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

        # Git tracking check if enabled
        git_status = None
        if check_git:
            # Check server-side .env file (informational only)
            git_status = check_git_tracking_safe(".env")
            # Add note that this is server-side check
            git_status["note"] = "Git check performed on server-side .env file"
            if git_status["is_tracked"]:
                errors.append("Git tracking error: .env file is tracked by git (should be in .gitignore)")

        # Sanitize error messages to prevent path leakage
        sanitized_errors = [sanitize_error_message(err) for err in errors]
        sanitized_warnings = [f"Unused variable in .env: {var}" for var in usage_unused]

        response_data = {
            'success': not sanitized_errors,
            'errors': sanitized_errors,
            'warnings': sanitized_warnings,
            'usage_missing': usage_missing,
            'usage_unused': usage_unused
        }

        # Add git status if checked
        if git_status:
            response_data['git_status'] = git_status

        return jsonify(response_data)

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
