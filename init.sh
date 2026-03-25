#!/bin/bash
# EnvLint Development Setup
set -e

cd "$(dirname "$0")"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install
echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -e ".[dev]" 2>/dev/null || pip install -q -e .

echo "EnvLint dev environment ready!"
echo "Starting web server on http://localhost:5000"
python -m envlint.web
