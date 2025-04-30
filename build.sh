#!/bin/bash
#########################################################################################
# Author : Achraf KHABAR
# Description : building the exe files and installing all dependancies needed by the app
# Date : 28/04/2025
# Version : 9.0
#########################################################################################

set -euo pipefail
set -x

EXEC_NAME="RobotTestRunner"

# 1. ENSURE PROPER ENVIRONMENT
echo "=== SETTING UP ENVIRONMENT ==="

# Activate virtual environment if exists
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
fi

# 2. VERIFY AND INSTALL DEPENDENCIES
echo "=== INSTALLING DEPENDENCIES ==="


python -c "import PyQt6" 2>/dev/null || {
    echo "PyQt6 not found. Installing..."
    pip install --upgrade pip
    pip install PyQt6 PyQt6-Charts
}

pip uninstall -y PyQt6 PyQt6-Charts PyQt6-Qt6
pip install PyQt6 PyQt6-Charts PyQt6-Qt6

# 3. WINDOWS CLEANUP
echo "=== CLEANING ENVIRONMENT ==="
taskkill /F /IM python* /T >nul 2>&1 || true
taskkill /F /IM pyinstaller* /T >nul 2>&1 || true
ping -n 2 127.0.0.1 >nul

# 4. CLEAN PREVIOUS BUILDS
echo "=== CLEANING PREVIOUS BUILDS ==="
rm -rf build/ *.spec || true
if [ -d "dist" ]; then
    rm -rf dist/* || true
    sleep 2
fi

# 5. GET QT PATHS (WITH FALLBACK)
echo "=== LOCATING QT LIBRARIES ==="
PYQT6_DIR=$(python -c "import os, PyQt6; print(os.path.dirname(PyQt6.__file__))")
QT_BIN_PATH="${PYQT6_DIR}/Qt6/bin"
QT_PLUGIN_PATH="${PYQT6_DIR}/Qt6/plugins"

# 6. VERIFY QT FILES
echo "=== VERIFYING QT FILES ==="
REQUIRED_FILES=(
    "${QT_BIN_PATH}/Qt6Core.dll"
    "${QT_BIN_PATH}/Qt6Gui.dll"
    "${QT_BIN_PATH}/Qt6Widgets.dll"
    "${QT_BIN_PATH}/Qt6Charts.dll"
    "${QT_PLUGIN_PATH}/platforms/qwindows.dll"
)

for FILE in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$FILE" ]; then
        echo "Missing required file: $FILE"
        echo "Reinstalling PyQt6..."
        pip uninstall -y PyQt6 PyQt6-Charts PyQt6-Qt6
        pip install PyQt6 PyQt6-Charts
        if [ ! -f "$FILE" ]; then
            echo "File still missing after reinstall: $FILE"
            exit 1
        fi
    fi
done

# 7. BUILD THE APPLICATION
echo "=== BUILDING EXECUTABLE ==="
pyinstaller --noconfirm --windowed \
  --name="$EXEC_NAME" \
  --icon=images/Logo_exe_grand.ico \
  --add-data="config.xml;." \
  --add-data="style/style.qss;style" \
  --add-data="images/*;images" \
  --add-data="${QT_BIN_PATH}/Qt6Core.dll;." \
  --add-data="${QT_BIN_PATH}/Qt6Gui.dll;." \
  --add-data="${QT_BIN_PATH}/Qt6Widgets.dll;." \
  --add-data="${QT_BIN_PATH}/Qt6Charts.dll;." \
  --add-data="${QT_PLUGIN_PATH}/platforms/qwindows.dll;PyQt6/Qt/plugins/platforms/" \
  --paths "${QT_BIN_PATH}" \
  --hidden-import PyQt6.QtCharts \
  --clean \
  main.py

# 8. COPY ADDITIONAL DEPENDENCIES
echo "=== COPYING ADDITIONAL FILES ==="
cp -v "${QT_BIN_PATH}/Qt6OpenGL.dll" "dist/${EXEC_NAME}/" || true

# 9. VERIFY FINAL BUILD
echo "=== VERIFYING BUILD ==="
if [ -f "dist/${EXEC_NAME}/${EXEC_NAME}.exe" ]; then
    echo "Build successful!"
    echo "Executable: dist/${EXEC_NAME}/${EXEC_NAME}.exe"
else
    echo "Build failed"
    exit 1
fi

echo "=== BUILD COMPLETED SUCCESSFULLY ==="