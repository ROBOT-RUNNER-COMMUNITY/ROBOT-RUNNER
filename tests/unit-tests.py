import unittest
import os
from PyQt6.QtWidgets import QApplication
from main import RobotTestRunner
from PyQt6.QtCore import Qt

app = QApplication([]) 


class TestRobotTestRunner(unittest.TestCase):
    def setUp(self):
        self.window = RobotTestRunner()

    def test_initial_ui_state(self):
        self.assertEqual(self.window.label.text(), "Select a folder containing .robot files")
        self.assertEqual(self.window.resultLabel.text(), "Test Results :")
        self.assertEqual(self.window.processInput.value(), 2)

    def test_select_directory(self):
        test_dir = os.getcwd()
        self.window.test_directory = test_dir
        self.window.load_tests()
        self.assertGreaterEqual(self.window.testList.count(), 0)

    def test_toggle_select_all_tests(self):
        item1 = self.window.testList.addItem("test1.robot")
        item2 = self.window.testList.addItem("test2.robot")

        QApplication.processEvents()

        self.window.selectAllCheckBox.setChecked(True)

        for i in range(self.window.testList.count()):
            self.assertEqual(self.window.testList.item(i).checkState(), Qt.CheckState.Checked)

    def test_run_tests_no_selection(self):
        self.window.run_tests()
        self.assertEqual(self.window.resultLabel.text(), "Please select a folder.")
        self.assertEqual(self.window.resultLabel.styleSheet(), "color: #ad402a")

    def test_run_tests_with_selection(self):
        self.window.testList.addItem("test1.robot")
        self.window.testList.addItem("test2.robot")
        
        QApplication.processEvents()
        
        self.window.testList.item(0).setCheckState(Qt.CheckState.Checked)

        self.assertEqual(self.window.testList.item(0).checkState(), Qt.CheckState.Checked)
        
        self.window.run_tests()

    def test_select_output_directory(self):
        test_dir = os.getcwd()
        self.window.output_directory = test_dir
        self.window.fileLabel.setText(f"Results stored in: {test_dir}")
        self.assertIn("Results stored in:", self.window.fileLabel.text())

    def test_clear_results_directory(self):
        self.window.output_directory = os.path.join(os.getcwd(), "Results")
        os.makedirs(self.window.output_directory, exist_ok=True)
        with open(os.path.join(self.window.output_directory, "dummy.txt"), "w") as f:
            f.write("test")

        self.window.clear_results_directory()
        self.assertEqual(len(os.listdir(self.window.output_directory)), 0)
        self.assertEqual(self.window.resultLabel.text(), "The Results folder has been emptied")


if __name__ == "__main__":
    unittest.main()
