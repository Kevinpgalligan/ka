from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
from PyQt5 import QtCore, QPalette
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit
import sys

class KaWidget(QWidget):
    key_pressed = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.initUI()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.key_pressed.emit(event.key())

    def initUI(self):
        self.resize(250, 200)
        self.setWindowTitle("ka")
        
        # https://doc.qt.io/qtforpython/PySide6/QtWidgets/QScrollArea.html
        #scroll_area = QScrollArea()
        #scrollArea.setBackgroundRole(QPalette.Dark)
        #scrollArea.setWidget(output_label)
        self.input_widget = QLineEdit(self)

        self.show()

def run_gui():
    print("QT version", QT_VERSION_STR)
    print("PyQT version", PYQT_VERSION_STR)
    app = QApplication([])
    w = KaWidget()
    def on_key(key):
        if key == QtCore.Qt.Key_Return:
            print(w.input_widget.text())
            #w.output_widget.setText()
            w.input_widget.clear()
    w.key_pressed.connect(on_key)
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui()
