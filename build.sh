#!/bin/bash
#####################################################################################
# Author : Achraf KHABAR
# Updated by : ChatGPT
# Description : Build Script for RobotTestRunner (with full PyQt6 packaging)
# Version : 2.3
#####################################################################################

set -e  # Stop the script on first error
set -x  # Debug mode: print each command

EXEC_NAME="RobotTestRunner"

# Install pyinstaller if missing
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install --upgrade pyinstaller
fi

echo "Cleaning old builds..."
rm -rf build dist "${EXEC_NAME}.spec" || true

# Detect OS type
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Linux/Mac detected"
    SEP=":"
else
    echo "Windows detected"
    SEP=";"
fi

# Get the path to the PyQt6 plugins directory
PYQT6_PLUGIN_PATH=$(python -c "from PyQt6.QtCore import QLibraryInfo, QLibraryInfoPath; print(QLibraryInfo.path(QLibraryInfoPath.PluginsPath))" || echo "")

# Check if plugin path is detected
if [ -z "$PYQT6_PLUGIN_PATH" ]; then
    echo "⚠️ Warning: PyQt6 plugin path not found. Continuing without explicit plugins."
    ADD_PLUGIN=""
else
    ADD_PLUGIN="--add-data \"${PYQT6_PLUGIN_PATH}${SEP}PyQt6/Qt/plugins\""
fi

# Build the executable
eval pyinstaller --noconfirm --windowed \
  --name "$EXEC_NAME" \
  --icon="images/Logo_exe_grand.ico" \
  --add-data "./config.xml${SEP}." \
  --add-data "./style/style.qss${SEP}style" \
  --add-data "./images/*${SEP}images" \
  $ADD_PLUGIN \
  --collect-all PyQt6 \
  --collect-submodules PyQt6 \
  --hidden-import PyQt6 \
  --hidden-import PyQt6.QtWidgets \
  --hidden-import PyQt6.QtGui \
  --hidden-import PyQt6.QtCore \
  main.py

# Check if success
if [ -f "dist/$EXEC_NAME.exe" ] || [ -f "dist/$EXEC_NAME" ]; then
    echo "✅ Executable created successfully in 'dist/'"
else
    echo "❌ Error creating executable"
    exit 1
fi
