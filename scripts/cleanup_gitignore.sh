#!/bin/bash
# Clean up files that should be ignored by git
# This removes them from git tracking but keeps them on disk

echo "Cleaning up git-tracked files that should be ignored..."

# Remove node_modules from git tracking if they exist
if [ -d "apps/frontend/node_modules" ]; then
    echo "Removing apps/frontend/node_modules from git tracking..."
    git rm -r --cached apps/frontend/node_modules 2>/dev/null || true
fi

if [ -d "apps/signaling/node_modules" ]; then
    echo "Removing apps/signaling/node_modules from git tracking..."
    git rm -r --cached apps/signaling/node_modules 2>/dev/null || true
fi

# Remove venv from git tracking if it exists
if [ -d "venv" ]; then
    echo "Removing venv from git tracking..."
    git rm -r --cached venv 2>/dev/null || true
fi

# Remove .env if it was tracked
if [ -f ".env" ]; then
    echo "Removing .env from git tracking..."
    git rm --cached .env 2>/dev/null || true
fi

echo "Done! Review changes with 'git status' and commit if needed."

