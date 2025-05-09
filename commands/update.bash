#!/bin/bash

# Update the main repository
echo "Pulling latest changes for the main repository..."
git pull || { echo "Failed to pull main repository."; exit 1; }

# Update submodules
echo "Updating submodules..."
git submodule update --init --recursive --remote || { echo "Failed to update submodules."; exit 1; }

# Run Aerich migrations and upgrades
echo "Choose an option for Aerich migrations and upgrades:"
echo "1) Delete the 'migrations' folder and reinitialize the database"
echo "2) Run migrations and upgrades"
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        echo "Deleting 'migrations' folder and reinitializing the database..."
        rm -rf migrations || { echo "Failed to delete 'migrations' folder."; exit 1; }
        aerich init-db || { echo "Aerich init-db failed."; exit 1; }
        ;;
    2)
        echo "Running Aerich migrations and upgrades..."
        aerich migrate || { echo "Aerich migration failed."; exit 1; }
        aerich upgrade || { echo "Aerich upgrade failed."; exit 1; }
        ;;
    *)
        echo "Running Aerich migrations and upgrades..."
        aerich migrate || { echo "Aerich migration failed."; exit 1; }
        aerich upgrade || { echo "Aerich upgrade failed."; exit 1; }
        ;;
esac

echo "Update complete!"