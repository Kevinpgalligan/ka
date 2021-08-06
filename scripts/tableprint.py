"""Print tables that list available features."""

import argparse
from ka.functions import FUNCTIONS

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("thing", choices=["units", "functions"])
    args = parser.parse_args()

    if args.thing == "units":
        print("oops, not yet supported.")
    elif args.thing == "functions":
        fs = sorted(FUNCTIONS.items(), key=lambda fdata: fdata[0])
        print_header(["Name", "Signatures"])
        for name, params in fs:
            sigs = [sig for f, sig in params]
            print_row([name, "<br/>".join(stringify_sig(sig) for sig in sigs)])

def print_header(headers):
    print("| " + " | ".join(headers) + " |")
    print("| " + " | ".join("---" for _ in headers) + " |")

def print_row(cells):
    print("| " + " | ".join(cells) + " |")

def stringify_sig(sig):
    return "(" + ", ".join(cls.__name__ for cls in sig) + ")"

if __name__ == "__main__":
    main()
