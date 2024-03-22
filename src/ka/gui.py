import sys
import io

from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR, Qt
from PyQt5.QtGui import QKeySequence
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QLabel,
    QScrollArea, QVBoxLayout, QMainWindow, QAction, QSizePolicy,
    QShortcut)

from .interpret import KA_VERSION, execute, ResultBox, stringify_result, get_functions_string, get_units_string
from .eval import EvalEnvironment

REPO_URL = "https://github.com/Kevinpgalligan/ka"
WSIZE = (600, 300)
HELP_SIZE = (400, 200)
DOC_SIZE = (500, 300)

def add_exit_shortcut(w):
    shortcut = QShortcut(QKeySequence("Ctrl+W"), w)
    shortcut.activated.connect(w.close)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(*WSIZE)
        self.setWindowTitle("ka")
        self.ka_widget = KaWidget()
        self.setCentralWidget(self.ka_widget)
        
        add_exit_shortcut(self)

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
        self.label.setText(f"""{get_version_string()}.<br>
ka is a calculator language. For more information, see <a href='{REPO_URL}'>{REPO_URL}</a>.<br>""")

        add_exit_shortcut(self)

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
Press Ctrl+W to quit the application.<br>
Press CTRL+Up or CTRL+Down to scroll through your command history.<br><br>
Functions: {get_functions_string()}
<br><br>
Units: {get_units_string()}""")
        add_exit_shortcut(self)

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
        self.output_box.setWordWrap(True)
        #self.output_box.setAlignment(Qt.AlignRight)

        # Make output area scrollable.
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.output_box)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.verticalScrollBar().rangeChanged.connect(self.scroll_to_bottom)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.input_widget = QLineEdit(self)
        self.input_widget.setFont(font)
        self.input_widget.resize(width, self.input_widget.height())
        self.input_widget.setFocus(True)

        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.input_widget)
        self.setLayout(layout)

    def scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum())

def get_version_string():
    return f"ka version {KA_VERSION}, QT version {QT_VERSION_STR}, PyQT version {PYQT_VERSION_STR}"

def run_gui():
    print(get_version_string())
    app = QApplication([])
    w = MainWindow()
    env = EvalEnvironment()
    displayed_stuff = []
    command_history = []
    command_index = 0
    def on_key(key):
        nonlocal command_index, command_history
        if key == QtCore.Qt.Key_Return:
            out = io.StringIO()
            txt = w.ka_widget.input_widget.text()
            command_history.append(txt)
            command_index = len(command_history)
            result_box = ResultBox()
            status = execute(txt, out=out, errout=out, env=env,
                             result_box=result_box, brackets_for_frac=True)
            displayed_stuff.extend([
                '<font color="grey">',
                txt,
                '</font>',
                '<br>'
            ])
            output_str = out.getvalue().replace("\n", "<br>").replace(" ", "&nbsp;")
            if status != 0:
                displayed_stuff.append('<font color="red">')
            displayed_stuff.append(output_str)
            if status != 0:
                displayed_stuff.append('</font>')
            displayed_stuff.append("<br>")
            displayed_str = "".join(displayed_stuff)
            w.ka_widget.output_box.setText(displayed_str)
            if result_box.value is not None:
                w.ka_widget.input_widget.setText(
                    stringify_result(result_box.value, brackets_for_frac=True))
            else:
                w.ka_widget.input_widget.clear()

    def previous_command():
        nonlocal command_index, command_history
        if command_index > 0:
            if command_index == len(command_history):
                # User might be currently composing a command, don't
                # wanna lose it.
                txt = w.ka_widget.input_widget.text()
                if txt:
                    command_history.append(txt)
            command_index -= 1
            w.ka_widget.input_widget.setText(command_history[command_index])
    def next_command():
        nonlocal command_index, command_history
        if command_index < len(command_history)-1:
            command_index += 1
            w.ka_widget.input_widget.setText(command_history[command_index])
    QShortcut(QKeySequence("Ctrl+Up"), w).activated.connect(previous_command)
    QShortcut(QKeySequence("Ctrl+Down"), w).activated.connect(next_command)
    w.ka_widget.key_pressed.connect(on_key)
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui()
