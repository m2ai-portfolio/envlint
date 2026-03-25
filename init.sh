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
pip install -e ".[dev]" 2>/dev/null || pip install -e .

echo "EnvLint dev environment ready!"
echo "Run: envlint --help"
