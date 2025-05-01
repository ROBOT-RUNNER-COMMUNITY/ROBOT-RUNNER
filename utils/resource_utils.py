import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".") 
    
    full_path = os.path.join(base_path, relative_path)
    print(f"Looking for resource at: {full_path}") 
    return full_path