from PyQt5.QtWidgets import QApplication, QFileDialog
import sys

def select_file_qt():
    """
    Opens a file picker using Qt (cross-platform).
    Returns the selected file path, or None if canceled.
    """
    app = QApplication.instance() or QApplication(sys.argv)
    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Select a file",
        "",
        "All files (*.*)"
    )
    return file_path if file_path else None