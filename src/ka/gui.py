import sys
import io

from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR, Qt
from PyQt5.QtGui import QKeySequence
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QLabel,
    QScrollArea, QVBoxLayout, QMainWindow, QAction, QSizePolicy,
    QShortcut)

from .interpret import KA_VERSION, execute
from .eval import EvalEnvironment

REPO_URL = "https://github.com/Kevinpgalligan/ka"
WSIZE = (400, 300)
HELP_SIZE = (400, 200)
DOC_SIZE = (500, 300)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(*WSIZE)
        self.setWindowTitle("ka")
        self.ka_widget = KaWidget()
        self.setCentralWidget(self.ka_widget)

        self.shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        self.shortcut.activated.connect(self.close)

        menu = self.menuBar()

        help_menu = menu.addMenu("&Help")
        about_action = QAction("&About", self)
        doc_action = QAction("&Documentation", self)

        self.help_window = HelpWindow()
        self.doc_window = DocWindow()

        about_action.triggered.connect(self.help_window.show)
        doc_action.triggered.connect(self.doc_window.show)

        help_menu.addAction(about_action)
        help_menu.addAction(doc_action)

class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(*HELP_SIZE)
        self.setWindowTitle("Help")
        self.label = QLabel(self)
        self.label.resize(self.size())
        self.label.setWordWrap(True)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label.setOpenExternalLinks(True)
        self.label.setText(f"""Version {KA_VERSION}.<br>
ka is a calculator language. For more information, see <a href='{REPO_URL}'>{REPO_URL}</a>.<br>
.""")

class DocWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(*DOC_SIZE)
        self.setWindowTitle("Documentation")
        self.label = QLabel(self)
        self.label.resize(self.size())
        self.label.setWordWrap(True)
        self.label.setOpenExternalLinks(True)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label.setText(f"""The full documentation for ka is available at <a href='{REPO_URL}'>{REPO_URL}</a>.<br><br>
Press Ctrl+W to quit the application.<br><br>
Functions: +, -, *, /, %, ^, sin, cos, tan, sqrt, ln, log10, log2, abs, floor, ceil, round, int, float, log, C, !, quit
<br><br>
Units: second (s), metre (m), gram (g), ampere (A), kelvin (K), mole (mol), candela (cd), hertz (Hz), radian (rad), steradian (sr), newton (N), pascal (Pa), joule (J), watt (W), coulomb (C), volt (V), farad (F), ohm (ohm), siemens (S), weber (Wb), tesla (T), henry (H), degC (degC), lumen (lm), lux (lx), becquerel (Bq), gray (Gy), sievert (Sv), katal (kat), minute (min), hour (h), day (d), astronomicalunit (au), degree (deg), hectare (ha), acre (acre), litre (l), tonne (t), dalton (Da), electronvolt (eV), lightyear (lj), parsec (pc), inch (in), foot (ft), yard (yd), mile (mi), nauticalmile (sm), teaspoon (tsp), tablespoon (tbsp), fluidounce (floz), cup (cup), gill (gill), pint (pt), quart (qt), gallon (gal), grain (gr), dram (dr), ounce (oz), pound (lb), horsepower (hp), bar (bar), calorie (cal)""")

class KaWidget(QWidget):
    key_pressed = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.initUI()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.key_pressed.emit(event.key())

    def initUI(self):
        width, height = WSIZE

        font = QtGui.QFont('monospace', 15)
        
        #self.output_box.resize(*wsize)
        self.output_box = QLabel()
        self.output_box.setFont(font)
        self.output_box.setStyleSheet("background-color: white;")
        self.output_box.setTextInteractionFlags(Qt.TextSelectableByMouse)
        #self.output_box.setAlignment(Qt.AlignRight)

        # Make output area scrollable.
        #self.scroll_area = QScrollArea()
        #self.scroll_area.setWidget(self.output_box)

        self.input_widget = QLineEdit()
        self.input_widget.setFont(font)
        self.input_widget.resize(width, self.input_widget.height())

        layout = QVBoxLayout()
        layout.addWidget(self.output_box)
        layout.addWidget(self.input_widget)
        self.setLayout(layout)

def run_gui():
    print("ka version", KA_VERSION)
    print("QT version", QT_VERSION_STR)
    print("PyQT version", PYQT_VERSION_STR)
    
    app = QApplication([])
    w = MainWindow()
    env = EvalEnvironment()
    def on_key(key):
        if key == QtCore.Qt.Key_Return:
            out = io.StringIO()
            txt = w.ka_widget.input_widget.text()
            result = execute(txt, out=out, errout=out, env=env)
            displayed_stuff = [
                '<font color="grey">',
                txt,
                '</font>',
                '<br><br>'
            ]
            output_str = out.getvalue().replace("\n", "<br>").replace(" ", "&nbsp;")
            if result != 0:
                displayed_stuff.append('<font color="red">')
            displayed_stuff.append(output_str)
            if result != 0:
                displayed_stuff.append('</font>')
            displayed_str = "".join(displayed_stuff)
            #print(repr(displayed_str))
            w.ka_widget.output_box.setText(displayed_str)
            w.ka_widget.input_widget.clear()
    w.ka_widget.key_pressed.connect(on_key)
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui()
