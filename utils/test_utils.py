import os
import subprocess
from robot.api import ExecutionResult
from PyQt6.QtCore import Qt, QTimer
from PyQt6 import QtCore
from PyQt6.QtGui import QMovie, QPixmap
from PyQt6.QtWidgets import QListWidgetItem
from utils.resource_utils import resource_path
from utils.display_utils import show_cross  # Now importing from display_utils

def load_tests(window):
    window.testList.clear()
    window.loadingLabel.show()
    loading_gif_path = resource_path("images/loading.gif")
    window.loading_movie = QMovie(loading_gif_path)
    window.loading_movie.setScaledSize(QtCore.QSize(45, 45))
    window.loadingLabel.setMovie(window.loading_movie)
    window.loading_movie.start()
    QTimer.singleShot(1500, lambda: populate_tests(window))

def populate_tests(window):
    window.loading_movie.stop()
    window.loadingLabel.clear()

    if window.test_directory:
        test_files = [file for file in os.listdir(window.test_directory) if file.endswith(".robot")]

        if not test_files:
            show_cross(window)
            window.label.setStyleSheet("color: #ad402a")
        else:
            for file in test_files:
                item = QListWidgetItem(file)
                item.setCheckState(Qt.CheckState.Unchecked)
                window.testList.addItem(item)

            window.label.setStyleSheet("color: green")
            check_icon_path = resource_path("images/check.png")
            check_pixmap = QPixmap(check_icon_path).scaled(27, 27, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            window.loadingLabel.setPixmap(check_pixmap)
            window.loadingLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

def run_tests(window):
    if not window.test_directory:
        window.resultLabel.setText("Please select a folder.")
        window.resultLabel.setStyleSheet("color: #ad402a")
        return
    
    if not window.output_directory:
        window.resultLabel.setText("Please select a location for the results.")
        window.resultLabel.setStyleSheet("color: #ad402a") 
        return 
    
    selected_tests = [os.path.join(window.test_directory, window.testList.item(i).text())
                     for i in range(window.testList.count())
                     if window.testList.item(i).checkState() == Qt.CheckState.Checked]
    
    if not selected_tests:
        window.resultLabel.setText("Please select at least one test.")
        window.resultLabel.setStyleSheet("color: #ad402a")
        return
    
    num_processes = window.processInput.text()
    report_title = "Robot Runner - Tests Autos"

    if num_processes == "1":
        command = ["robot", "-d", window.output_directory] + selected_tests            
    else:
        command = ["pabot", "--processes", num_processes, "--outputdir", window.output_directory, 
                  "--reporttitle", report_title] + selected_tests
    
    subprocess.run(command, cwd=window.test_directory, capture_output=True, text=True)
    
    output_path = os.path.join(window.output_directory, "output.xml")
    result = ExecutionResult(output_path)
     
    if result.suite.statistics.failed >= 1:
        window.resultLabel.setText(f"TOTAL: {result.suite.statistics.total} | PASS: {result.suite.statistics.passed} | FAIL: {result.suite.statistics.failed}")
        window.resultLabel.setStyleSheet("color: #ad402a")
    else:
        window.resultLabel.setText(f"TOTAL: {result.suite.statistics.total} | PASS: {result.suite.statistics.passed} | FAIL: {result.suite.statistics.failed}")
        window.resultLabel.setStyleSheet("color: green")

def open_report(window):
    report_path = os.path.join(window.output_directory, "report.html")
    if os.path.exists(report_path):
        os.system(f'start "" "{report_path}"')

def open_log(window):
    log_path = os.path.join(window.output_directory, "log.html")
    if os.path.exists(log_path):
        os.system(f'start "" "{log_path}"')