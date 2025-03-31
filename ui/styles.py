import os
from utils.resource_utils import resource_path

def apply_styles(widget):
    style_file = resource_path("style/style.qss")
    if os.path.exists(style_file):
        with open(style_file, "r") as file:
            widget.setStyleSheet(file.read())