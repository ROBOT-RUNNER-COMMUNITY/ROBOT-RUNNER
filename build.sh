#!/bin/bash
#####################################################################################
# Author : Achraf KHABAR
# Date : 2023-10-01
# Description : Script de construction pour le projet RobotTestRunner
# Version : 1.2
#####################################################################################

set -x

EXEC_NAME="RobotTestRunner"

if ! command -v pyinstaller &> /dev/null; then
    pip install --upgrade pyinstaller
fi

echo "Nettoyage des anciens fichiers..."
rm -rf build dist "${EXEC_NAME}.spec"

if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Linux"
    SEP=":"
else
    echo "Windows"
    SEP=";"
fi

# Forcer l'import de tous les modules nécessaires
pyinstaller --noconfirm --onefile --windowed --name "$EXEC_NAME" \
    --add-data "./config.xml${SEP}." \
    --add-data "./style/style.qss${SEP}style" \
    --add-data "./images/*${SEP}images" \
    --hidden-import PyQt6 \
    --hidden-import PyQt6.QtWidgets \
    --hidden-import PyQt6.QtGui \
    --hidden-import PyQt6.QtCore \
    --hidden-import numpy \
    --hidden-import pandas \
    --hidden-import matplotlib \
    --hidden-import robotframework \
    --icon=images/Logo_exe_grand.ico main.py

if [ -f "dist/$EXEC_NAME" ] || [ -f "dist/$EXEC_NAME.exe" ]; then
    echo "L'exécutable a été généré avec succès dans le dossier 'dist/'"
else
    echo "Erreur lors de la génération de l'exécutable"
    exit 1
fi
