import os
import os.path
from pathlib import Path

if os.name == "nt":
    # Windows.
    SYSTEM_CONFIG_DIR = Path(Path.home().joinpath("AppData", "Local", "ka"))
else:
    # Posix.
    SYSTEM_CONFIG_DIR = Path(Path.home().joinpath(".config", "ka"))

CONFIG_PATH = SYSTEM_CONFIG_DIR.joinpath("config")
DEFAULT_HISTORY_PATH = SYSTEM_CONFIG_DIR.joinpath("history")
DEFAULT_CURRENCY_PATH = SYSTEM_CONFIG_DIR.joinpath("currency")

CONFIG = dict()
HAVE_READ = False

class ConfigProperty:
    def __init__(self, name, default, num=False, boolean=False):
        self.name = name
        self.default = default
        self.num = num
        self.boolean = boolean

class ConfigProperties:
    PRECISION = ConfigProperty("precision", 6, num=True)
    FONT_SIZE = ConfigProperty("font-size", 15, num=True)
    WINDOW_WIDTH = ConfigProperty("window-width", 600, num=True)
    WINDOW_HEIGHT = ConfigProperty("window-height", 400, num=True)
    DEFAULT_SHORTCUT_UP = ConfigProperty("shortcut-up", "Ctrl+Up")
    DEFAULT_SHORTCUT_DOWN = ConfigProperty("shortcut-down", "Ctrl+Down")
    DEFAULT_SHORTCUT_FUNCTIONS = ConfigProperty("shortcut-functions", "Ctrl+F")
    DEFAULT_SHORTCUT_UNITS = ConfigProperty("shortcut-units", "Ctrl+Q")
    DEFAULT_SHORTCUT_PREFIXES = ConfigProperty("shortcut-prefixes", "Ctrl+P")
    DEFAULT_SHORTCUT_CLOSE = ConfigProperty("shortcut-close", "Ctrl+W")
    SAVE_HISTORY = ConfigProperty("save-history", True, boolean=True)
    HISTORY_PATH = ConfigProperty("history-path", DEFAULT_HISTORY_PATH)
    PROMPT = ConfigProperty("prompt", ">>>")
    CURRENCY_PATH = ConfigProperty("currency-path", DEFAULT_CURRENCY_PATH)
    BASE_CURRENCY = ConfigProperty("base-currency", "eur")

def get(prop):
    global HAVE_READ
    if not HAVE_READ:
        read_config(CONFIG_PATH)
    return CONFIG.get(prop.name, prop.default)

def read_config(path, error_out=None):
    global HAVE_READ
    HAVE_READ = True
    def printerr(s):
        if error_out:
            print(s, file=error_out)
    if not (os.path.exists(path) and os.path.isfile(path)):
        return
    props_obj = ConfigProperties()
    props = [props_obj.__getattribute__(x)
             for x in dir(props_obj)
             if not x.startswith("_")]
    with open(path, "r") as f:
        for line in f.readlines():
            items = line.split("=")
            if len(items) < 2:
                continue
            name, val = map(lambda x: x.strip(), items)
            prop = next((prop for prop in props if prop.name == name),
                        None)
            if prop:
                if prop.num:
                    try:
                        val = int(val)
                    except ValueError:
                        printerr(f"WARNING: expecting integer value for config variable '{name}'.")
                        continue
                if prop.boolean:
                    if val == "true":
                        val = True
                    elif val == "false":
                        val = False
                    else:
                        printerr(f"WARNING: expecting boolean value (true/false) for config variable '{name}'.")
                        continue
                CONFIG[name] = val
            else:
                printerr(f"WARNING: unknown config variable '{name}'.")
