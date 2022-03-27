import sys

from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QLabel,
    QScrollArea)

from .interpret import KA_VERSION, execute
from .eval import EvalEnvironment

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
        
        self.output_box = QLabel(parent=self)
        self.output_box.resize(150, 190)
        self.output_box.setStyleSheet("background-color: white;")
        # Make output area scrollable.
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.output_box)

        self.input_widget = QLineEdit(self)

        self.show()

def run_gui():
    print("ka version", KA_VERSION)
    print("QT version", QT_VERSION_STR)
    print("PyQT version", PYQT_VERSION_STR)
    
    app = QApplication([])
    w = KaWidget()
    env = EvalEnvironment()
    def on_key(key):
        if key == QtCore.Qt.Key_Return:
            out = io.StringIO()
            result = execute(w.input_widget.text(), , out=out, errout=out, env=env)
            if result != 0:
                # TODO: Set text to red.
                pass
            # TODO: get output from `out` and write it.
            #w.output_widget.setText()
            # TODO: Restore text colour?
            w.input_widget.clear()
    w.key_pressed.connect(on_key)
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui()
