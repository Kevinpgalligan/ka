import argparse
import sys

from .interpret import (run_interpreter, execute,
    print_units, print_functions, print_unit_info,
    print_function_info, print_prefixes)
from .currency import scrape_and_store_rates_to
import ka.config
from .config import ConfigProperties

def add_and_store_argument(parser, flaglist, name, **kwargs):
    flaglist.append(name)
    parser.add_argument(name, **kwargs)

def main():
    ka.config.read_config(ka.config.CONFIG_PATH)
    parser = argparse.ArgumentParser(description="A calculator language. Run with no arguments to start the interpreter.")
    parser.add_argument("x", nargs="?", help="The statements to evaluate.")

    flaglist = ["-h", "--help"]
    add_and_store_argument(parser, flaglist, "--script", help="Run a script file containing Ka code.")
    add_and_store_argument(parser, flaglist, "--scrape-currency-to", help="Scrape currency data and dump to the given file.")
    add_and_store_argument(parser, flaglist, "--units", action="store_true", help="List all available units.")
    add_and_store_argument(parser, flaglist, "--functions", action="store_true", help="List all available functions.")
    add_and_store_argument(parser, flaglist, "--unit", help="See the details of a particular unit.")
    add_and_store_argument(parser, flaglist, "--function", help="See the details of a particular function.")
    add_and_store_argument(parser, flaglist, "--gui", help="Start the Graphical User Interface.", action="store_true")
    add_and_store_argument(parser, flaglist, "--prefixes", action="store_true", help="List all available unit prefixes, their symbols and multipliers.")

    raw_args = sys.argv[1:]
    if len(raw_args) == 1 and raw_args[0] not in flaglist:
        sys.exit(execute(raw_args[0])) 

    args = parser.parse_args()

    if args.units:
        print_units()
    elif args.prefixes:
        print_prefixes()
    elif args.functions:
        print_functions()
    elif args.unit:
        print_unit_info(args.unit)
    elif args.function:
        print_function_info(args.function)
    elif args.gui:
        from .gui import run_gui
        run_gui()
    elif args.script:
        run_script(args.script)
    elif args.scrape_currency_to:
        print("Scraping currency data...")
        scrape_and_store_rates_to(args.scrape_currency_to)
    else:
        run_interpreter()

def run_script(path):
    with open(path, "r") as f:
        s = f.read()
        execute(s)

if __name__ == "__main__":
    main()
