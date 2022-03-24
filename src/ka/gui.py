from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
from PyQt5.QtWidgets import QApplication, QWidget
import sys

def run_gui():
    print(QT_VERSION_STR)
    print(PYQT_VERSION_STR)
    app = QApplication([])
    w = QWidget()
    w.resize(250, 200)
    w.setWindowTitle("ka")
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui()
