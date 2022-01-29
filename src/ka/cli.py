import argparse
import sys

from .tokens import tokenise, UnknownTokenError
from .parse import parse_tokens, pretty_print_parse_tree, ParsingError
from .eval import eval_parse_tree
from .types import Quantity
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
        result = eval_parse_tree(parse_tree)
        if result is None:
            print()
        else:
            display_result(result)

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
