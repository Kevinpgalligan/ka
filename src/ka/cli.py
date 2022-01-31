import argparse
import sys
from fractions import Fraction as frac

from .tokens import tokenise, UnknownTokenError
from .parse import parse_tokens, ParsingError
from .eval import eval_parse_tree, EvalError, EvalEnvironment
from .types import Quantity
from .functions import (FUNCTIONS, UnknownFunctionError,
    NoMatchingFunctionSignatureError, IncompatibleQuantitiesError,
    make_sig_printable)
from .units import UNITS, lookup_unit

ERROR_CONTEXT_SIZE = 5
INDENT = 2

PROMPT = ">>> "
KA_VERSION = "1.0"

def main():
    parser = argparse.ArgumentParser(description="A calculator language.")
    parser.add_argument("x", nargs="?", help="The statements to evaluate.")
    parser.add_argument("--units", action="store_true", help="Print all available units.")
    parser.add_argument("--functions", action="store_true", help="Print all available functions.")
    parser.add_argument("--unit", help="See the details of a particular unit.")
    parser.add_argument("--function", help="See the details of a particular function.")
    args = parser.parse_args()

    if args.units:
        print_units()
    elif args.functions:
        print_functions()
    elif args.unit:
        print_unit_info(args.unit)
    elif args.function:
        print_function_info(args.function)
    elif args.x:
        sys.exit(execute(args.x, EvalEnvironment()))
    else:
        run_interpreter()

def print_units():
    print(", ".join(f"{unit.singular_name} ({unit.symbol})"
                    for unit in UNITS))

def print_unit_info(name):
    unit = lookup_unit(name)
    if unit is None:
        print("Unknown unit.")
    else:
        print("                     Name:", unit.singular_name)
        print("              Plural name:", unit.plural_name)
        print("                   Symbol:", unit.symbol)
        print("               Quantities:", ", ".join(unit.quantities))
        print("    Base units equivalent:", unit.quantity_vector.prettified())
        print("  Magnitude in base units:", unit.multiple)
        print("   Offset from base units:", unit.offset)

def print_functions():
    print(", ".join(name for name in FUNCTIONS.keys()))

def print_function_info(name):
    if name not in FUNCTIONS:
        print("Unknown function.")
    else:
        signatures = list(map(lambda x: x[1], FUNCTIONS[name]))
        print("                   Name:", name)
        print("          Documentation:", "to-do")
        types_prompt = "Accepted argument types: "
        print(types_prompt, end="")
        for i, sig in enumerate(signatures):
            if i > 0:
                print(" "*len(types_prompt), end="")
            print("(" + ", ".join(make_sig_printable(sig)) + ")")

def run_interpreter():
    env = EvalEnvironment()
    print("ka version", KA_VERSION)
    while True:
        execute(input(PROMPT), env)

def execute(s, env):
    try:
        tokens = tokenise(s)
    except UnknownTokenError as e:
        error("Unknown token!", e.index, s)
        return 1
    try:
        parse_tree = parse_tokens(tokens)
    except ParsingError as e:
        # 3 cases:
        #  a) there are no tokens, it's the empty string.
        #  b) we read all the tokens and then needed another one.
        #  c) unexpected token.
        if not tokens:
            index = 0
        elif e.token_index >= len(tokens):
            index = tokens[-1].end_index_excl
        else:
            index = tokens[e.token_index].begin_index_incl
        error(e.message, index, s)
        return 1
    try:
        result = eval_parse_tree(parse_tree, env)
        if result is None:
            print()
        else:
            display_result(result)
    except EvalError as e:
        print_err(e.message)
        return 1
    except UnknownFunctionError as e:
        print_err(f"Unknown function: '{e.name}'")
        global FUNCTIONS
        alternatives = find_close_matches(e.name, FUNCTIONS.keys())
        if alternatives:
            print_err("  You may have meant:", ", ".join(alternatives))
        return 1
    except NoMatchingFunctionSignatureError as e:
        print_err(f"Function '{e.name}' does not accept {printable_signature(e.attempted_signature)}.")
        print_err("It does accept:")
        for sig in e.actual_signatures:
            print_err("   ", printable_signature(sig))
        return 1
    except IncompatibleQuantitiesError as e:
        print_err("Tried to combine two incompatible quantities.")
        print_err("The first is a quantity of:")
        print_err("   ", e.qv1.prettified())
        print_err("The second is a quantity of:")
        print_err("   ", e.qv2.prettified())
        return 1

def printable_signature(sig):
    return "(" + ", ".join(sig) + ")"

def find_close_matches(s, ss):
    return set(ss) & adjacent_strings([s])

def adjacent_strings(xs):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    final = set()
    for x in xs:
        final |= set([x[:i] + x[i+1:] for i in range(len(x))])
        final |= set([x[:i] + c + x[i:]
                     for c in alphabet
                     for i in range(len(x)+1)])
        final |= set([x[:i] + c + x[i+1:]
                      for c in alphabet
                      for i in range(len(x))])
    return final

def print_err(*msgs):
    print(*msgs, file=sys.stderr)

def error(msg, index, s):
    error_lines = [msg]
    if s:
        context_low_index = max(0, index-ERROR_CONTEXT_SIZE)
        context_high_index = min(len(s), index+ERROR_CONTEXT_SIZE+1)
        left_fade = "" if context_low_index == 0 else "..."
        right_fade = "" if context_high_index == len(s) else "..."
        error_lines.append("")
        error_lines.append(
            " "*INDENT + left_fade + s[context_low_index:context_high_index] + right_fade)
        error_lines.append(
            " "*(INDENT+len(left_fade)+index-context_low_index) + "^")
    print("\n".join(error_lines), file=sys.stderr)

def display_result(r):
    if isinstance(r, Quantity):
        print(r.mag, r.qv.prettified(), end="")
        if isinstance(r.mag, frac):
            print("    (" + str(float(r.mag)) + " " + r.qv.prettified() + ")", end="")
        print()
    elif isinstance(r, frac):
        print(r, "    (" + str(float(r)) + ")")
    else:
        print(r)
