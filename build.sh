#!/bin/bash
set -e

echo "Building static files and running migrations..."

# 1. If Vercel/uv created a virtual environment already, use it!
if [ -f "/vercel/path0/.vercel/python/.venv/bin/python" ]; then
    echo "Using existing @vercel/python virtual environment..."
    PYTHON="/vercel/path0/.vercel/python/.venv/bin/python"
elif [ -f ".venv/bin/python" ]; then
    echo "Using existing .venv virtual environment..."
    PYTHON=".venv/bin/python"
else
    echo "No virtual environment found on system path. Creating one for build..."
    python3 -m venv .build_venv || python -m venv .build_venv
    PYTHON=".build_venv/bin/python"
    $PYTHON -m pip install --upgrade pip
    $PYTHON -m pip install -r requirements.txt
fi

echo "Running database migrations with $PYTHON..."
$PYTHON manage.py migrate --noinput

echo "Collecting static files with $PYTHON..."
$PYTHON manage.py collectstatic --noinput --clear
