#!/bin/bash

# Modern cleanup script for Insight Journey Backend
# Removes temporary files, logs, and build artifacts

echo "🧹 Starting cleanup process..."

# 1. Python cache and build artifacts
echo "🐍 Cleaning Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# 2. Log files
echo "📋 Cleaning log files..."
rm -f *.log
rm -f app.log
rm -f api.log
rm -f transcript_processing.log
rm -f debug.log
rm -f error.log

# 3. Temporary files
echo "🗑️  Removing temporary files..."
rm -f cookies.txt
rm -f .DS_Store
find . -name ".DS_Store" -delete 2>/dev/null || true
rm -f *.tmp
rm -f *.temp

# 4. Test artifacts
echo "🧪 Cleaning test artifacts..."
rm -rf .pytest_cache
rm -f .coverage
rm -rf htmlcov/
rm -rf test-results/

# 5. IDE files
echo "💻 Cleaning IDE files..."
rm -rf .vscode/settings.json 2>/dev/null || true
rm -rf .idea/ 2>/dev/null || true
rm -f *.swp
rm -f *.swo

# 6. Build artifacts
echo "🏗️  Cleaning build artifacts..."
rm -rf build/
rm -rf dist/

# 7. Environment files (keep .env but remove others)
echo "🔧 Cleaning old environment files..."
rm -f .env.bak
rm -f .env.old
rm -f .env.backup

# 8. Docker artifacts
echo "🐳 Cleaning Docker artifacts..."
rm -f Dockerfile.bak
rm -f docker-compose.override.yml.bak

echo "✅ Cleanup complete!"
echo "📊 Summary:"
echo "  - Python cache files removed"
echo "  - Log files cleared"
echo "  - Temporary files deleted"
echo "  - Test artifacts cleaned"
echo "  - IDE files removed"
echo "  - Build artifacts cleared" 