#!/bin/bash

echo "Cleaning up unnecessary documentation files..."

# Create backup directory
mkdir -p docs/backup

# Move files to backup instead of deleting them
mv docs/ARCHITECTURE.md docs/backup/ 2>/dev/null || true
mv docs/DEPLOYMENT.md docs/backup/ 2>/dev/null || true
mv docs/FRONTEND_INTEGRATION.md docs/backup/ 2>/dev/null || true

# Back up API docs
mkdir -p docs/backup/api
cp -r docs/api/* docs/backup/api/ 2>/dev/null || true

# Back up other folders
for dir in docs/configuration docs/integration docs/architecture docs/getting-started; do
  if [ -d "$dir" ]; then
    mkdir -p docs/backup/$(basename $dir)
    cp -r $dir/* docs/backup/$(basename $dir)/ 2>/dev/null || true
  fi
done

# Remove backed up directories
rm -rf docs/api
rm -rf docs/configuration
rm -rf docs/integration
rm -rf docs/architecture
rm -rf docs/getting-started

echo "Documentation cleaned up. Old files backed up to docs/backup/"
echo "New simplified documentation available at docs/DOCUMENTATION.md" 