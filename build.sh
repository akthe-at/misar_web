#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pdm install

# Convert static asset files
pdm manage collectstatic --no-input

# Apply any outstanding database migrations
pdm manage migrate
