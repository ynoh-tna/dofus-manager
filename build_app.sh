#!/bin/bash
# Build script for Dofus Window Manager
# Compile the app, rename it, add icon, and clean up

echo "🔨 Building Dofus Window Manager..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Get the directory where this script is located
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📦 Compiling application..."

# Build with PyInstaller - avec chemins absolus
pyinstaller \
    --name dofus_manager \
    --onefile \
    --windowed \
    --add-data "${PROJECT_DIR}/core:core" \
    --add-data "${PROJECT_DIR}/ui:ui" \
    --collect-all PyQt6 \
    --distpath "${PROJECT_DIR}/dist" \
    --workpath "${PROJECT_DIR}/build" \
    --specpath "${PROJECT_DIR}/build" \
    "${PROJECT_DIR}/main.py"

if [ $? -ne 0 ]; then
    echo "❌ Compilation failed!"
    exit 1
fi

echo "✅ Compilation successful!"

# Move executable to project root
if [ -f "${PROJECT_DIR}/dist/dofus_manager" ]; then
    cp "${PROJECT_DIR}/dist/dofus_manager" "${PROJECT_DIR}/dofus_manager"
    chmod +x "${PROJECT_DIR}/dofus_manager"
    echo "✅ Executable copied to project root"
fi

# Clean up unnecessary files
echo "🧹 Cleaning up..."

rm -rf "${PROJECT_DIR}/build"
rm -rf "${PROJECT_DIR}/dist"

# Remove .pyc and __pycache__ files if they exist
find "${PROJECT_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find "${PROJECT_DIR}" -type f -name "*.pyc" -delete 2>/dev/null

echo "✅ Build complete!"
echo ""
echo "📍 Executable location: ${PROJECT_DIR}/dofus_manager"
echo ""
echo "To run the application:"
echo "  ${PROJECT_DIR}/dofus_manager"
echo ""