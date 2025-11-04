#!/bin/bash
# scripts/setup-pre-commit.sh

# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run pre-commit on all files (optional)
# pre-commit run --all-files

echo "Pre-commit hooks installed successfully!"
