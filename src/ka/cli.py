import argparse
import sys

from .interpret import (run_interpreter, execute,
    print_units, print_functions, print_unit_info,
    print_function_info)

def add_and_store_argument(parser, flaglist, name, **kwargs):
    flaglist.append(name)
    parser.add_argument(name, **kwargs)

def main():
    parser = argparse.ArgumentParser(description="A calculator language. Run with no arguments to start the interpreter.")
    parser.add_argument("x", nargs="?", help="The statements to evaluate.")

    flaglist = ["-h", "--help"]
    add_and_store_argument(parser, flaglist, "--units", action="store_true", help="List all available units.")
    add_and_store_argument(parser, flaglist, "--functions", action="store_true", help="List all available functions.")
    add_and_store_argument(parser, flaglist, "--unit", help="See the details of a particular unit.")
    add_and_store_argument(parser, flaglist, "--function", help="See the details of a particular function.")
    add_and_store_argument(parser, flaglist, "--gui", help="Start the Graphical User Interface.", action="store_true")

    raw_args = sys.argv[1:]
    if len(raw_args) == 1 and raw_args[0] not in flaglist:
        sys.exit(execute(raw_args[0])) 

    args = parser.parse_args()

    if args.units:
        print_units()
    elif args.functions:
        print_functions()
    elif args.unit:
        print_unit_info(args.unit)
    elif args.function:
        print_function_info(args.function)
    elif args.gui:
        from .gui import run_gui
        run_gui()
    else:
        run_interpreter()
