import os
import shutil
from PyQt6.QtWidgets import QFileDialog

def select_directory(window):
    dir_path = QFileDialog.getExistingDirectory(window, "Select a folder")
    if dir_path:
        window.test_directory = dir_path
        window.label.setText(f"Selected: {dir_path}")
        os.makedirs(os.path.join(dir_path, "Results"), exist_ok=True)
        window.testList.clear()
        from utils.test_utils import load_tests  # Import here to avoid circular import
        load_tests(window)
    else:
        from utils.display_utils import show_cross  # Import here
        show_cross(window)
        window.label.setStyleSheet("color: #ad402a")

def select_output_directory(window):
    dir_path = QFileDialog.getExistingDirectory(window, "Select a results folder")
    if dir_path:
        window.output_directory = dir_path
        window.fileLabel.setText(f"Results saved in: {dir_path}")
        window.fileLabel.setStyleSheet("color: green")

def clear_results_directory(window):
    if window.output_directory and os.path.exists(window.output_directory):
        for file in os.listdir(window.output_directory):
            file_path = os.path.join(window.output_directory, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                window.resultLabel.setText(f"Deletion error: {str(e)}")
                window.resultLabel.setStyleSheet("color: #ad402a")
                return
        
        window.resultLabel.setText("The Results folder has been emptied")
        window.resultLabel.setStyleSheet("color: green")
    else:
        window.resultLabel.setText("No Results folder found")
        window.resultLabel.setStyleSheet("color: #ad402a")