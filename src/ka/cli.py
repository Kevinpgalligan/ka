import argparse

from .tokens import tokenise
from .parse import parse_tokens, pretty_print_parse_tree
from .eval import eval_parse_tree

def main():
    parser = argparse.ArgumentParser(description="A calculator language.")
    parser.add_argument("x", help="The statements to evaluate.")
    parser.add_argument("--show-tree",
                        "-s",
                        action="store_true",
                        help="Whether to print the parse tree instead of evaluating it.")
    args = parser.parse_args()
    tokens = tokenise(args.x)
    parse_tree = parse_tokens(tokens)
    if args.show_tree:
        pretty_print_parse_tree(parse_tree)
    else:
        print(eval_parse_tree(parse_tree))
