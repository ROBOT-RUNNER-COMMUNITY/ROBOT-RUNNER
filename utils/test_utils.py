import os
import subprocess
from openpyxl import Workbook
from robot.api import ExecutionResult
from PyQt6.QtCore import Qt, QTimer
from PyQt6 import QtCore
from PyQt6.QtGui import QMovie, QPixmap
from PyQt6.QtWidgets import QListWidgetItem
from utils.resource_utils import resource_path
from utils.display_utils import show_cross  # Now importing from display_utils
from openpyxl.chart import BarChart, Reference
import traceback
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
 
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
        window.resultLabel.setStyleSheet("color: none")
        window.resultLabel.setText("Veuillez sélectionner un dossier.")
        window.resultLabel.setStyleSheet("color: #ad402a; font: bold")
        return
       
    if not window.output_directory:
        window.resultLabel.setStyleSheet("color: none")
        window.resultLabel.setText("Veuillez sélectionner un emplacement pour les résultats.")
        window.resultLabel.setStyleSheet("color: #ad402a; font: bold")
        return
       
    selected_tests = [os.path.join(window.test_directory, window.testList.item(i).text())
                        for i in range(window.testList.count())
                        if window.testList.item(i).checkState() == Qt.CheckState.Checked]
       
    if not selected_tests:
        window.resultLabel.setStyleSheet("color: none")
        window.resultLabel.setText("Veuillez sélectionner au moins un test.")
        window.resultLabel.setStyleSheet("color: #ad402a; font: bold")
        return
       
    num_processes = window.processInput.text()
    repport_title = "AUTOS TESTS - REPORT"
    log_title = "AUTOS TESTS - LOG"
 
    if num_processes == 1:
        command = ["robot", "-d", window.output_directory] + selected_tests            
        output_path = os.path.join(window.output_directory, "output.xml")
    else :
        command = ["pabot", "--processes", num_processes, "--outputdir", window.output_directory, "--reporttitle", repport_title, "--logtitle", log_title] + selected_tests
    subprocess.run(command, cwd=window.test_directory, capture_output=True, text=True)
       
    output_path = os.path.join(window.output_directory, "output.xml")
    result = ExecutionResult(output_path)
         
    if result.suite.statistics.failed >= 1:
        window.resultLabel.setStyleSheet("color: none")
        window.resultLabel.setText(f"Total: {result.suite.statistics.total} | Passés: {result.suite.statistics.passed} | Échoués: {result.suite.statistics.failed}")
        window.resultLabel.setStyleSheet("color: #ad402a; font: bold")
    else:
        window.resultLabel.setStyleSheet("color: none")
        window.resultLabel.setText(f"Total: {result.suite.statistics.total} | Passés: {result.suite.statistics.passed} | Échoués: {result.suite.statistics.failed}")
        window.resultLabel.setStyleSheet("color: green; font: bold")        
 
def open_report(window):
    report_path = os.path.join(window.output_directory, "report.html")
    if os.path.exists(report_path):
        os.system(f'start "" "{report_path}"')
 
def open_log(window):
    log_path = os.path.join(window.output_directory, "log.html")
    if os.path.exists(log_path):
        os.system(f'start "" "{log_path}"')

def export_results(window):
    try:
        if not hasattr(window, 'output_directory') or not window.output_directory:
            window.resultLabel.setText("Output directory not set!")
            window.resultLabel.setStyleSheet("color: #ad402a")
            return

        output_xml = os.path.join(window.output_directory, "output.xml")
        if not os.path.exists(output_xml):
            window.resultLabel.setText("Run tests first to generate output.xml!")
            window.resultLabel.setStyleSheet("color: #ad402a")
            return

        result = ExecutionResult(output_xml)
        wb = Workbook()
        ws = wb.active
        ws.title = "Test Results"

        headers = ["Suite Name", "Test Name", "Status", "Duration (s)"]
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="D3D3D3", fill_type="solid")

        passed_count = 0
        failed_count = 0

        for suite in result.suite.suites:
            for test in suite.tests:
                status = "Passed" if test.passed else "Failed"
                duration = getattr(test.elapsed_time, 'total_seconds', lambda: 0)()
                ws.append([suite.name, test.name, status, duration])

                status_cell = ws.cell(row=ws.max_row, column=3)
                if test.passed:
                    passed_count += 1
                    status_cell.fill = PatternFill(start_color="C6EFCE", fill_type="solid")
                    status_cell.font = Font(color="006100")
                else:
                    failed_count += 1
                    status_cell.fill = PatternFill(start_color="FFC7CE", fill_type="solid")
                    status_cell.font = Font(color="9C0006")

        chart_data_start = ws.max_row + 2
        ws.append(["Status", "Count"])
        ws.append(["Passed", passed_count])
        ws.append(["Failed", failed_count])

        chart = BarChart()
        chart.type = "col"
        chart.style = 10
        chart.title = "Test Results Summary"
        chart.y_axis.title = "Number of Tests"
        chart.x_axis.title = "Status"
        chart.grouping = "clustered"
        chart.overlap = 0
        chart.width = 15
        chart.height = 10

        data = Reference(ws,
                         min_col=2,  # "Count" column
                         min_row=chart_data_start + 0,
                         max_row=chart_data_start + 1)

        cats = Reference(ws,
                         min_col=1,  # "Status" column
                         min_row=chart_data_start + 0,
                         max_row=chart_data_start + 1)

        chart.add_data(data, titles_from_data=False)
        chart.set_categories(cats)

        ws.add_chart(chart, "F2")

        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = max_len + 2

        excel_path = os.path.join(window.output_directory, 'test_results.xlsx')
        wb.save(excel_path)

        if os.path.exists(excel_path):
            window.resultLabel.setText(f"Report exported to {excel_path}")
            window.resultLabel.setStyleSheet("color: green")
            os.startfile(excel_path)
        else:
            window.resultLabel.setText("Failed to create Excel file")
            window.resultLabel.setStyleSheet("color: #ad402a")

    except Exception as e:
        window.resultLabel.setText(f"Export error: {str(e)}")
        window.resultLabel.setStyleSheet("color: #ad402a")
        print(f"Error details:\n{traceback.format_exc()}")