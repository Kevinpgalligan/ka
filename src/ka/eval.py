import math
from .types import number
from .functions import dispatch

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
    QUANTITY = "quantity"
    UNIT_SIGNATURE = "unit-signature"

class EvalEnvironment:
    def __init__(self):
        self._variables = CONSTANTS.copy()

    def set_variable(self, name, value):
        self._variables[name] = value
        return value

    def get_variable(self, name):
        if name not in self._variables:
            # TODO custom exception
            raise Exception("fuck")
        return self._variables[name]

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
        return dispatch(node.label, child_values)
    if mode == EvalModes.ASSIGNMENT:
        return env.set_variable(node.label, child_values[0])
    if mode == EvalModes.STATEMENTS:
        return child_values[-1] if child_values else None
    if mode == EvalModes.QUANTITY:
        raise Exception("TODO")
    if mode == EvalModes.UNIT_SIGNATURE:
        raise Exception("TODO")
    raise Exception("TODO unknown eval mode")
