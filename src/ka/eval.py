import math
from .types import number
from .functions import FUNCTIONS

CONSTANTS = {
    "e": number(math.e),
    "pi": number(math.pi)
}

class EvalModes:
    LABEL_IS_VALUE = "label-is-value"
    VARIABLE = "variable"
    FUNCALL = "funcall"
    ASSIGNMENT = "assignment"
    STATEMENTS = "statements"

class EvalEnvironment:
    def __init__(self):
        self._variables = CONSTANTS.copy()
        self._functions = FUNCTIONS.copy()

    def set_variable(self, name, value):
        self._variables[name] = value
        return value

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
    return eval_node(root, EvalEnvironment())

def eval_node(node, env):
    return eval_based_on_mode(
        node,
        env,
        [eval_node(child, env) for child in node.children])

def eval_based_on_mode(node, env, child_values):
    mode = node.eval_mode
    if mode == EvalModes.LABEL_IS_VALUE:
        return node.label
    if mode == EvalModes.VARIABLE:
        return env.get_variable(node.label)
    if mode == EvalModes.FUNCALL:
        return call_function(env.get_function(node.label), child_values)
    if mode == EvalModes.ASSIGNMENT:
        # Assume that the node is labelled "x=" if we're
        # assigning a value to the variable "x". And there
        # should be only 1 child. Should fix this kludge.
        return env.set_variable(node.label[:-1], child_values[0])
    if mode == EvalModes.STATEMENTS:
        return child_values[-1] if child_values else None
    raise Exception("TODO unknown eval mode")

def call_function(f, args):
    # TODO:
    # 1. incorrect number of args 
    # 2. coerce types if necessary.
    # 3. just call it?
    # Might need some complicated typing stuff.
    # Like, find closest-matching type signature.
    return 0
