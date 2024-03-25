import os.path
from pathlib import Path

CONFIG_PATH = Path.home().joinpath(".config", "ka", "config")

PRECISION = 6

def read_config(path, error_out=None):
    global PRECISION
    def printerr(s):
        if error_out:
            print(s, file=error_out)
    if not (os.path.exists(path) and os.path.isfile(path)):
        return
    with open(path, "r") as f:
        for line in f.readlines():
            items = line.split("=")
            if len(items) < 2:
                continue
            name, val = items
            if name == "precision":
                try:
                    val = int(val)
                    PRECISION = val
                except:
                    printerr("WARNING: expecting integer value for 'precision' config.")
            else:
                printerr(f"WARNING: unknown config variable '{name}'.")
