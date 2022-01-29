import argparse
import sys

from .tokens import tokenise, UnknownTokenError
from .parse import parse_tokens, pretty_print_parse_tree, ParsingError
from .eval import eval_parse_tree, EvalError
from .types import Quantity
from .functions import (FUNCTIONS, UnknownFunctionError,
    NoMatchingFunctionSignatureError, IncompatibleQuantitiesError)
from fractions import Fraction as frac

ERROR_CONTEXT_SIZE = 5
INDENT = 2

def main():
    parser = argparse.ArgumentParser(description="A calculator language.")
    parser.add_argument("x", help="The statements to evaluate.")
    parser.add_argument("--tree",
                        "-t",
                        action="store_true",
                        help="Whether to print the parse tree instead of evaluating it.")
    args = parser.parse_args()
    s = args.x
    try:
        tokens = tokenise(s)
    except UnknownTokenError as e:
        error("Unknown token!", e.index, s)
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
    if args.tree:
        pretty_print_parse_tree(parse_tree)
    else:
        try:
            result = eval_parse_tree(parse_tree)
            if result is None:
                print()
            else:
                display_result(result)
        except EvalError as e:
            print_err(e.message)
            sys.exit(1)
        except UnknownFunctionError as e:
            print_err(f"Unknown function: '{e.name}'")
            global FUNCTIONS
            alternatives = find_close_matches(e.name, FUNCTIONS.keys())
            if alternatives:
                print_err("  You may have meant:", ", ".join(alternatives))
            sys.exit(1)
        except NoMatchingFunctionSignatureError as e:
            print_err(f"Function '{e.name}' does not accept {printable_signature(e.attempted_signature)}.")
            print_err("It does accept:")
            for sig in e.actual_signatures:
                print_err("   ", printable_signature(sig))
            sys.exit(1)
        except IncompatibleQuantitiesError as e:
            print_err("Tried to combine two incompatible quantities.")
            print_err("The first is a quantity of:")
            print_err("   ", e.qv1.prettified())
            print_err("The second is a quantity of:")
            print_err("   ", e.qv2.prettified())
            sys.exit(1)

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
    sys.exit(1)

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
