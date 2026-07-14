#!/bin/bash
set -e

echo "Building static files and running migrations..."

# Create virtual environment
if command -v uv >/dev/null 2>&1; then
    echo "Using uv to create virtual environment..."
    uv venv .build_venv --python 3.10 || uv venv .build_venv
else
    echo "Using python venv..."
    python3 -m venv .build_venv
fi

PYTHON="$PWD/.build_venv/bin/python"

echo "Upgrading pip..."
$PYTHON -m pip install --upgrade pip

echo "Installing cmake..."
$PYTHON -m pip install cmake==3.31.6

echo "Installing requirements..."
$PYTHON -m pip install -r requirements.txt

echo "Running migrations..."
$PYTHON manage.py migrate --noinput

echo "Collecting static files..."
$PYTHON manage.py collectstatic --noinput --clear