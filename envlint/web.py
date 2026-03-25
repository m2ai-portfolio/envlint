"""Flask web interface for EnvLint (for testing purposes)."""

import json
from flask import Flask, render_template, request, jsonify
from .schema import parse_env_content, load_schema_from_dict, validate_schema
from .models import Schema

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

    Returns JSON with:
        - success: boolean
        - errors: list of error messages
    """
    try:
        data = request.get_json()
        env_content = data.get('env_content', '')
        schema_content = data.get('schema_content', '')

        # Parse schema from JSON string
        try:
            schema_data = json.loads(schema_content)
        except json.JSONDecodeError as e:
            return jsonify({
                'success': False,
                'errors': [f'Invalid schema JSON: {str(e)}']
            }), 400

        # Load schema and validate patterns
        schema = load_schema_from_dict(schema_data)

        # Parse env content
        env_vars = parse_env_content(env_content)

        # Validate
        errors = validate_schema(env_vars, schema)

        # Sanitize error messages to prevent path leakage
        sanitized_errors = [sanitize_error_message(err) for err in errors]

        if sanitized_errors:
            return jsonify({
                'success': False,
                'errors': sanitized_errors
            })
        else:
            return jsonify({
                'success': True,
                'errors': []
            })

    except ValueError as e:
        # Sanitize error message
        error_msg = sanitize_error_message(str(e))
        return jsonify({
            'success': False,
            'errors': [f'Validation error: {error_msg}']
        }), 400
    except Exception as e:
        # Sanitize error message
        error_msg = sanitize_error_message(str(e))
        return jsonify({
            'success': False,
            'errors': [f'Unexpected error: {error_msg}']
        }), 500


def run_server(port=5000):
    """Run the Flask development server."""
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    run_server()
