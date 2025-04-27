#!/bin/bash
#####################################################################################
# Author : Achraf KHABAR
# Updated by : ChatGPT
# Description : Build Script for RobotTestRunner (with full PyQt6 packaging)
# Version : 2.2
#####################################################################################

set -x

EXEC_NAME="RobotTestRunner"

# Install pyinstaller if missing
if ! command -v pyinstaller &> /dev/null; then
    pip install --upgrade pyinstaller
fi

echo "Cleaning old builds..."
rm -rf build dist "${EXEC_NAME}.spec"

# Detect OS type
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Linux/Mac detected"
    SEP=":"
else
    echo "Windows detected"
    SEP=";"
fi

# Get the path to the PyQt6 plugins directory
PYQT6_PLUGIN_PATH=$(python -c "import PyQt6.QtCore; print(PyQt6.QtCore.QLibraryInfo.path(PyQt6.QtCore.QLibraryInfo.PluginsPath))")

# Build the executable
pyinstaller --noconfirm --onefile --windowed \
  --name "$EXEC_NAME" \
  --icon=images/Logo_exe_grand.ico \
  --add-data "./config.xml;." \
  --add-data "./style/style.qss${SEP}style" \
  --add-data "./images/*${SEP}images" \
  --add-data "${PYQT6_PLUGIN_PATH}${SEP}PyQt6/Qt/plugins" \
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
