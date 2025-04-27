#!/bin/bash
#####################################################################################
# Author : Achraf KHABAR
# Date : 2023-10-01
# Description : Script de construction pour le projet RobotTestRunner
# Version : 1.2
#####################################################################################

set -x

EXEC_NAME="RobotTestRunner"

# Installer PyInstaller si nécessaire
if ! command -v pyinstaller &> /dev/null; then
    pip install --upgrade pyinstaller
fi

echo "Nettoyage des anciens fichiers..."
rm -rf build dist "${EXEC_NAME}.spec" python-embed vc_redist.x64.exe

echo "Téléchargement des dépendances..."
# Télécharger VC++ Redistributable
curl -L -o vc_redist.x64.exe "https://aka.ms/vs/17/release/vc_redist.x64.exe"

echo "Préparation de Python embarqué..."
PYTHON_EMBED_VERSION="3.10.11"
PYTHON_EMBED_URL="https://www.python.org/ftp/python/${PYTHON_EMBED_VERSION}/python-${PYTHON_EMBED_VERSION}-embed-amd64.zip"

mkdir -p python-embed
curl -o python-embed.zip "$PYTHON_EMBED_URL"
unzip python-embed.zip -d python-embed
rm python-embed.zip

# Configurer le fichier _pth pour inclure site-packages
echo "python310.zip
.
import site
" > python-embed/python310._pth

# Télécharger get-pip
curl -o python-embed/get-pip.py https://bootstrap.pypa.io/get-pip.py

# Créer un script d'initialisation
echo "@echo off
\"%~dp0python.exe\" get-pip.py
\"%~dp0Scripts\\pip.exe\" install numpy pandas matplotlib PyQt6
" > python-embed/initialize.bat

# Déterminer le séparateur de chemin selon l'OS
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Linux/MacOS"
    SEP=":"
else
    echo "Windows"
    SEP=";"
fi

echo "Construction de l'exécutable avec PyInstaller..."
pyinstaller --noconfirm --onefile --windowed --name "$EXEC_NAME" \
    --add-data "./config.xml;." \
    --add-data "./style/style.qss${SEP}style" \
    --add-data "./images/*${SEP}images" \
    --add-data "./python-embed/*${SEP}python" \
    --add-data "./vc_redist.x64.exe;." \
    --icon=images/Logo_exe_grand.ico main.py

if [ -f "dist/$EXEC_NAME" ] || [ -f "dist/$EXEC_NAME.exe" ]; then
    echo "L'exécutable a été généré avec succès dans le dossier 'dist/'"
else
    echo "Erreur lors de la génération de l'exécutable"
    exit 1
fi