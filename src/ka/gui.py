import sys
import io
import html

from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR, Qt
from PyQt5.QtGui import QKeySequence
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QLabel,
    QScrollArea, QVBoxLayout, QMainWindow, QAction, QSizePolicy,
    QShortcut, QHBoxLayout, QComboBox)

from .interpret import (KA_VERSION, execute, ResultBox, stringify_result,
    get_functions_string, get_units_string, format_unit_info,
    format_function_info)
from .eval import EvalEnvironment
from .functions import FUNCTION_NAMES
from .units import UNITS, PREFIXES

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

        self.help_window = HelpWindow()
        help_menu = menu.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.help_window.show)

        help_menu.addAction(about_action)

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
ka is a calculator language. For documentation, see <a href='{REPO_URL}'>{REPO_URL}</a>.<br>""")

class HintBar(QWidget):
    display_fn_signal = QtCore.pyqtSignal(int)
    display_unit_signal = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        cb_functions = QComboBox(self)
        cb_functions.addItem("Functions / Ops")
        cb_functions.addItems(FUNCTION_NAMES)
        cb_units = QComboBox(self)
        cb_units.addItem("Units")
        cb_units.addItems([f"{u.singular_name} ({u.symbol})" for u in UNITS])
        cb_prefixes = QComboBox(self)
        cb_prefixes.addItem("Prefixes")
        cb_prefixes.addItems([f"{p.name_prefix} ({p.symbol_prefix}, {p.base}^{p.exponent})"
                              for p in PREFIXES])

        cb_functions.currentIndexChanged.connect(self.display_fn_signal)
        cb_units.currentIndexChanged.connect(self.display_unit_signal)

        selection_area = QHBoxLayout()
        selection_area.addWidget(cb_functions)
        selection_area.addWidget(cb_units)
        selection_area.addWidget(cb_prefixes)
        self.setLayout(selection_area)
        
class KaWidget(QWidget):
    key_pressed = QtCore.pyqtSignal(int)
    display_fn_signal = QtCore.pyqtSignal(int)
    display_unit_signal = QtCore.pyqtSignal(int)

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

        self.hint_bar = HintBar(self)
        self.hint_bar.display_fn_signal.connect(self.display_fn_signal)
        self.hint_bar.display_unit_signal.connect(self.display_unit_signal)

        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.input_widget)
        layout.addWidget(self.hint_bar)
        self.setLayout(layout)

        add_exit_shortcut(self)

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
    def add_display_text(txt):
        displayed_stuff.extend([
            '<font color="grey">',
            html.escape(txt).replace("\n", "<br>").replace(" ", "&nbsp;"),
            '</font>',
            '<br>'
        ])
    def update_display():
        displayed_str = "".join(displayed_stuff)
        w.ka_widget.output_box.setText(displayed_str)
    def on_key(key):
        nonlocal command_index, command_history
        if key == QtCore.Qt.Key_Return:
            out = io.StringIO()
            txt = w.ka_widget.input_widget.text()
            command_history.append(txt)
            command_index = len(command_history)
            result_box = ResultBox()
            assigned_box = ResultBox()
            status = execute(txt, out=out, errout=out, env=env,
                             result_box=result_box, brackets_for_frac=True,
                             assigned_box=assigned_box)
            add_display_text(txt)
            output_str = html.escape(out.getvalue())
            if status != 0:
                displayed_stuff.append('<font color="red">')
            displayed_stuff.append(output_str)
            if status != 0:
                displayed_stuff.append('</font>')
            displayed_stuff.append("<br>")
            update_display()
            if assigned_box.value is not None:
                w.ka_widget.input_widget.setText(assigned_box.value)
            elif result_box.value is not None:
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

    def display_fn(i):
        if i > 0:
            add_display_text(format_function_info(FUNCTION_NAMES[i-1]))
            add_display_text("")
            update_display()
    def display_unit(i):
        if i > 0:
            add_display_text(format_unit_info(UNITS[i-1]))
            add_display_text("\n")
            update_display()
    QShortcut(QKeySequence("Ctrl+Up"), w).activated.connect(previous_command)
    QShortcut(QKeySequence("Ctrl+Down"), w).activated.connect(next_command)
    w.ka_widget.key_pressed.connect(on_key)
    w.ka_widget.display_fn_signal.connect(display_fn)
    w.ka_widget.display_unit_signal.connect(display_unit)
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui()
