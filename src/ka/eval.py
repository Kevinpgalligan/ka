import math
from .types import number

CONSTANTS = {
    "e": number(math.e),
    "pi": number(math.pi)
}

FUNCTIONS = {
    # TODO Argument conversion somewhere.
    "cos": lambda n: math.cos(n.x)
}

class EvalEnvironment:
    def __init__(self):
        self._variables = CONSTANTS.copy()
        self._functions = FUNCTIONS.copy()

    def set_variable(self, name, value):
        self._variables[name] = value

    def get_variable(self, name):
        if name not in self._variables:
            # TODO custom exception
            raise Exception("fuck")
        return self._variables[name]

    def get_function(self, name):
        if name not in self._functions:
            # TODO proper exception
            raise Exception("fuck")
        return self._functions[name]

def eval_parse_tree(root):
    # Make a copy of the built-in constants, so they
    # can't be overwritten.
    return root.eval(EvalEnvironment())
