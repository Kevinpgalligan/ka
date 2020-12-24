import math
from .types import number

CONSTANTS = {
    "e": number(math.e),
    "pi": number(math.pi)
}

def eval_parse_tree(root):
    # Make a copy of the built-in constants, so they
    # can't be overwritten.
    return root.eval(CONSTANTS.copy())
