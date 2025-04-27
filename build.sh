#!/bin/bash
#####################################################################################
# Author : Achraf KHABAR
# Date : 2023-10-01
# Description : Script de construction pour le projet RobotTestRunner
# Version : 2.0 (Fixed PyQt6 issue)
#####################################################################################

set -x

EXEC_NAME="RobotTestRunner"

# Install pyinstaller if not available
if ! command -v pyinstaller &> /dev/null; then
    pip install --upgrade pyinstaller
fi

echo "Nettoyage des anciens fichiers..."
rm -rf build dist "${EXEC_NAME}.spec"

# Detect system type
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Linux/Mac"
    SEP=":"
else
    echo "Windows"
    SEP=";"
fi

# Build the executable
pyinstaller --noconfirm --onefile --windowed \
  --name "$EXEC_NAME" \
  --add-data "./config.xml;." \
  --add-data "./style/style.qss${SEP}style" \
  --add-data "./images/*${SEP}images" \
  --add-data "$(python -c 'import PyQt6.QtCore; print(PyQt6.QtCore.QLibraryInfo.path(PyQt6.QtCore.QLibraryInfo.PluginsPath))')${SEP}PyQt6/Qt/plugins" \
  --collect-all PyQt6 \
  --icon=images/Logo_exe_grand.ico \
  main.py

# Check if the executable exists
if [ -f "dist/$EXEC_NAME" ] || [ -f "dist/$EXEC_NAME.exe" ]; then
    echo "✅ L'exécutable a été généré avec succès dans le dossier 'dist/'"
else
    echo "❌ Erreur lors de la génération de l'exécutable"
    exit 1
fi
