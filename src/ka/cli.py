import argparse
import sys

from .tokens import tokenise, UnknownTokenError
from .parse import parse_tokens, pretty_print_parse_tree
from .eval import eval_parse_tree

ERROR_CONTEXT_SIZE = 5
INDENT = 2

def main():
    parser = argparse.ArgumentParser(description="A calculator language.")
    parser.add_argument("x", help="The statements to evaluate.")
    parser.add_argument("--show-tree",
                        "-s",
                        action="store_true",
                        help="Whether to print the parse tree instead of evaluating it.")
    args = parser.parse_args()
    try:
        tokens = tokenise(args.x)
    except UnknownTokenError as e:
        alert_unknown_token(e, args.x)
        sys.exit(1)
    parse_tree = parse_tokens(tokens)
    if args.show_tree:
        pretty_print_parse_tree(parse_tree)
    else:
        print(eval_parse_tree(parse_tree))

def alert_unknown_token(e, s):
    context_low_index = max(0, e.index-ERROR_CONTEXT_SIZE)
    context_high_index = min(len(s), e.index+ERROR_CONTEXT_SIZE+1)
    left_fade = "" if context_low_index == 0 else "..."
    right_fade = "" if context_high_index == len(s) else "..."
    print("\n".join([
        "Unknown token!",
        "",
        " "*INDENT + left_fade + s[context_low_index:context_high_index] + right_fade,
        " "*(INDENT+len(left_fade)+e.index-context_low_index) + "^"]))
