import sys
import io
import html
import re

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
from .config import ConfigProperties
import ka.config

REPO_URL = "https://github.com/Kevinpgalligan/ka"
HELP_SIZE = (400, 200)
DOC_SIZE = (500, 300)

WHITESPACE_AT_START = re.compile("^[ ]+", re.MULTILINE)

def add_exit_shortcut(w):
    shortcut = QShortcut(QKeySequence(ka.config.get(ConfigProperties.DEFAULT_SHORTCUT_CLOSE)), w)
    shortcut.activated.connect(w.close)

def make_scroll(subwidget):
    w = QScrollArea()
    w.setWidget(subwidget)
    w.setWidgetResizable(True)
    w.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    return w

class MainWindow(QMainWindow):
    def __init__(self, size, font_size):
        super().__init__()
        self.resize(*size)
        self.setWindowTitle("ka")
        self.ka_widget = KaWidget(self, size, font_size)
        self.setCentralWidget(self.ka_widget)
        
        add_exit_shortcut(self)

        menu = self.menuBar()

        self.about_window = AboutWindow()
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.about_window.show)

        self.shortcuts_window = ShortcutsWindow()
        shortcuts_action = QAction("&Shortcuts", self)
        shortcuts_action.triggered.connect(self.shortcuts_window.show)

        help_menu = menu.addMenu("&Help")
        help_menu.addAction(about_action)
        help_menu.addAction(shortcuts_action)

def add_help_text(w, txt):
    w.label = QLabel(w)
    w.label.setFont(QtGui.QFont('monospace', 15))
    w.label.setStyleSheet("background-color: white;")
    w.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
    w.label.resize(w.size())
    w.label.setWordWrap(True)
    w.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    w.label.setOpenExternalLinks(True)
    w.label.setText(txt)
    w.scroll = make_scroll(w.label)
    layout = QVBoxLayout()
    layout.addWidget(w.scroll)
    w.setLayout(layout)

class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(*HELP_SIZE)
        self.setWindowTitle("About")
        add_help_text(self, f"""{get_version_string()}.

For documentation, see {REPO_URL}.""")
        add_exit_shortcut(self)

class ShortcutsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(*HELP_SIZE)
        self.setWindowTitle("Shortcuts")
        add_help_text(self, f"""Default keyboard shortcuts are as follows. They can be adjusted in the config file.

* Close window: {ka.config.get(ConfigProperties.DEFAULT_SHORTCUT_CLOSE)}.
* Previous command in history: {ka.config.get(ConfigProperties.DEFAULT_SHORTCUT_UP)}.
* Next command in history: {ka.config.get(ConfigProperties.DEFAULT_SHORTCUT_DOWN)}.
* Open list of functions: {ka.config.get(ConfigProperties.DEFAULT_SHORTCUT_FUNCTIONS)}.
* Open list of units: {ka.config.get(ConfigProperties.DEFAULT_SHORTCUT_UNITS)}.
* Open list of prefixes: {ka.config.get(ConfigProperties.DEFAULT_SHORTCUT_PREFIXES)}.
""")
        add_exit_shortcut(self)

class HintBar(QWidget):
    display_fn_signal = QtCore.pyqtSignal(int)
    display_unit_signal = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)

        self.cb_functions = QComboBox(self)
        self.cb_functions.addItem("Functions / Ops")
        self.cb_functions.addItems(FUNCTION_NAMES)
        self.cb_units = QComboBox(self)
        self.cb_units.addItem("Units")
        self.cb_units.addItems([f"{u.singular_name} ({u.symbol})" for u in UNITS])
        self.cb_prefixes = QComboBox(self)
        self.cb_prefixes.addItem("Prefixes")
        self.cb_prefixes.addItems([f"{p.name_prefix} ({p.symbol_prefix}, {p.base}^{p.exponent})"
                              for p in PREFIXES])

        self.cb_functions.currentIndexChanged.connect(self.display_fn_signal)
        self.cb_units.currentIndexChanged.connect(self.display_unit_signal)

        selection_area = QHBoxLayout()
        selection_area.addWidget(self.cb_functions)
        selection_area.addWidget(self.cb_units)
        selection_area.addWidget(self.cb_prefixes)
        self.setLayout(selection_area)

    def show_functions(self):
        self.cb_functions.showPopup()

    def show_units(self):
        self.cb_units.showPopup()

    def show_prefixes(self):
        self.cb_prefixes.showPopup()
 
class KaWidget(QWidget):
    key_pressed = QtCore.pyqtSignal(int)
    display_fn_signal = QtCore.pyqtSignal(int)
    display_unit_signal = QtCore.pyqtSignal(int)

    def __init__(self, parent, size, font_size):
        super().__init__(parent)
        self.initUI(size, font_size)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.key_pressed.emit(event.key())

    def initUI(self, size, font_size):
        width, height = size

        font = QtGui.QFont('monospace', font_size)
        
        #self.output_box.resize(*wsize)
        self.output_box = QLabel()
        self.output_box.setFont(font)
        self.output_box.setStyleSheet("background-color: white;")
        self.output_box.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.output_box.setWordWrap(True)
        #self.output_box.setAlignment(Qt.AlignLeft)

        # Make output area scrollable.
        self.scroll_area = make_scroll(self.output_box)
        self.scroll_area.verticalScrollBar() \
            .rangeChanged \
            .connect(self.scroll_to_bottom)

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

    def show_functions(self):
        self.hint_bar.show_functions()

    def show_units(self):
        self.hint_bar.show_units()

    def show_prefixes(self):
        self.hint_bar.show_prefixes()

    def scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum())

def get_version_string():
    return f"ka version {KA_VERSION}, QT version {QT_VERSION_STR}, PyQT version {PYQT_VERSION_STR}"

def escape_whitespace(txt):
    # This preserves formatting-related whitespace that is
    # found at the start of a line, so that it doesn't get thrown out
    # during HTML formatting. We don't want to escape all the whitespace,
    # however, because then word wrap doesn't work.
    result = io.StringIO()
    i = 0
    for m in WHITESPACE_AT_START.finditer(txt):
        result.write(txt[i:m.start()])
        for _ in range(m.end()-m.start()):
            result.write("&nbsp;")
        i = m.end()
    result.write(txt[i:])
    return result.getvalue()

def run_gui():
    print(get_version_string())
    size = (ka.config.get(ConfigProperties.WINDOW_WIDTH),
            ka.config.get(ConfigProperties.WINDOW_HEIGHT))
    font_size = ka.config.get(ConfigProperties.FONT_SIZE)
    app = QApplication([])
    w = MainWindow(size, font_size)
    env = EvalEnvironment()
    displayed_stuff = []
    command_history = []
    command_index = 0
    def add_display_text(txt):
        displayed_stuff.extend([
            '<font color="grey">',
            escape_whitespace(html.escape(txt)).replace("\n", "<br>"),
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
    QShortcut(QKeySequence(ka.config.get(ConfigProperties.DEFAULT_SHORTCUT_UP)), w) \
        .activated \
        .connect(previous_command)
    QShortcut(QKeySequence(ka.config.get(ConfigProperties.DEFAULT_SHORTCUT_DOWN)), w) \
        .activated \
        .connect(next_command)
    QShortcut(QKeySequence(ka.config.get(ConfigProperties.DEFAULT_SHORTCUT_FUNCTIONS)), w) \
        .activated \
        .connect(w.ka_widget.show_functions)
    QShortcut(QKeySequence(ka.config.get(ConfigProperties.DEFAULT_SHORTCUT_UNITS)), w) \
        .activated \
        .connect(w.ka_widget.show_units)
    QShortcut(QKeySequence(ka.config.get(ConfigProperties.DEFAULT_SHORTCUT_PREFIXES)), w) \
        .activated \
        .connect(w.ka_widget.show_prefixes)
    w.ka_widget.key_pressed.connect(on_key)
    w.ka_widget.display_fn_signal.connect(display_fn)
    w.ka_widget.display_unit_signal.connect(display_unit)
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui()
