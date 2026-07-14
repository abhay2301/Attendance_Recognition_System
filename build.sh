#!/bin/bash
set -e

echo "Building static files and running migrations..."

# Check if uv is available on Vercel build machine for fast and clean installation
if command -v uv &> /dev/null || [ -x "/usr/local/bin/uv" ] || [ -x "$HOME/.cargo/bin/uv" ]; then
    if command -v uv &> /dev/null; then
        UV_CMD=$(command -v uv)
    elif [ -x "/usr/local/bin/uv" ]; then
        UV_CMD="/usr/local/bin/uv"
    else
        UV_CMD="$HOME/.cargo/bin/uv"
    fi
    echo "Found uv at $UV_CMD. Using uv to set up virtual environment and dependencies..."
    
    $UV_CMD venv .build_venv --python 3.10 || $UV_CMD venv .build_venv
    PYTHON=".build_venv/bin/python"
    
    echo "Installing cmake first using uv..."
    $UV_CMD pip install cmake==3.31.6
    
    echo "Installing requirements.txt using uv..."
    $UV_CMD pip install -r requirements.txt
else
    echo "uv not found. Falling back to standard python venv and pip..."
    python3 -m venv .build_venv || python -m venv .build_venv
    PYTHON=".build_venv/bin/python"
    
    $PYTHON -m pip install --upgrade pip
    echo "Installing cmake first via pip..."
    $PYTHON -m pip install cmake==3.31.6
    echo "Installing requirements.txt via pip..."
    $PYTHON -m pip install -r requirements.txt
fi

echo "Running database migrations with $PYTHON..."
$PYTHON manage.py migrate --noinput

echo "Collecting static files with $PYTHON..."
$PYTHON manage.py collectstatic --noinput --clear
