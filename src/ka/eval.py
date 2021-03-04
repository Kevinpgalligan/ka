import math
from .types import Quantity, number, is_number
from .functions import dispatch, multiply, add
from .units import lookup_unit, QSPACE, UnitSignature

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

class EvalError(Exception):
    def __init__(self, message):
        self.message = message

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
    if mode == EvalModes.UNIT_SIGNATURE:
        return make_unit_signature(node.value)
    if mode == EvalModes.QUANTITY:
        return make_quantity(child_values[0], child_values[1])
    raise EvalError(f"Unknown evaluation mode: '{mode}' (This is a bug!)")

def make_unit_signature(unit_exp_pairs):
    offset = 0
    multiple = 1
    qv = QSPACE.get_zero()
    for name, exp in unit_exp_pairs:
        unit = lookup_unit(name)
        if unit is None:
            raise EvalError(f"Unknown unit '{name}'. (Remember that it's case-sensitive).")
        qv *= unit.quantity_vector ** exp
        multiple *= unit.multiple ** exp
        offset = unit.offset
        if offset != 0 and len(unit_exp_pairs) > 1:
            raise EvalError(f"Can't combine unit '{name}' with other units, since it has an offset.")
        if offset != 0 and exp != 1:
            raise EvalError(f"Can't raise unit '{name}' to a power because it has an offset.")
    return UnitSignature(qv, multiple, offset)

def make_quantity(magnitude, unit_signature):
    if not is_number(magnitude):
        raise EvalError(f"Tried to add units to '{type(magnitude)}', which isn't a magnitude.")
    return Quantity(add(
                        multiply(magnitude, number(unit_signature.multiple)),
                        number(unit_signature.offset)),
                    unit_signature.quantity_vector)
