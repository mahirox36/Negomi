#!/bin/bash

# Update the main repository
echo "Pulling latest changes for the main repository..."
git pull origin main || { echo "Failed to pull main repository."; exit 1; }

# Update submodules
echo "Updating submodules..."
git submodule update --init --recursive || { echo "Failed to update submodules."; exit 1; }
git submodule foreach git pull origin main || { echo "Failed to pull submodule updates."; exit 1; }

# Run Aerich migrations and upgrades
echo "Running Aerich migrations and upgrades..."
aerich migrate || { echo "Aerich migration failed."; exit 1; }
aerich upgrade || { echo "Aerich upgrade failed."; exit 1; }

echo "Update complete!"