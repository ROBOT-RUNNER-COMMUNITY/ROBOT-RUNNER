import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QMessageBox
from ui.main_window import RobotTestRunner

def setup_embedded_environment():
    """Configure l'environnement Python embarqué et installe les dépendances si nécessaire"""
    try:
        # Chemin vers le Python embarqué
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        python_embed_path = os.path.join(base_path, 'python')
        
        if os.path.exists(python_embed_path):
            # Vérifier si pip est installé
            pip_installed = os.path.exists(os.path.join(python_embed_path, 'Scripts', 'pip.exe'))
            
            if not pip_installed:
                # Installer pip
                subprocess.call([
                    os.path.join(python_embed_path, 'python.exe'),
                    os.path.join(python_embed_path, 'get-pip.py'),
                    '--user'
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Vérifier les packages requis
            required_packages = ['numpy', 'pandas', 'matplotlib', 'PyQt6']
            for package in required_packages:
                package_path = os.path.join(python_embed_path, 'Lib', 'site-packages', package)
                if not os.path.exists(package_path):
                    # Installer les dépendances manquantes
                    subprocess.call([
                        os.path.join(python_embed_path, 'Scripts', 'pip.exe'),
                        'install', package
                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Configurer le PATH
            os.environ['PATH'] = python_embed_path + os.pathsep + os.environ['PATH']
            sys.path.insert(0, python_embed_path)
            
    except Exception as e:
        QMessageBox.critical(None, "Erreur d'initialisation", 
                           f"Erreur lors de la configuration de l'environnement : {str(e)}")

if __name__ == "__main__":
    # Configurer l'environnement avant de lancer l'application
    if getattr(sys, 'frozen', False):
        setup_embedded_environment()
    
    app = QApplication(sys.argv)
    window = RobotTestRunner()
    window.show()
    sys.exit(app.exec())