import math
from .types import Quantity, number, is_number
from .functions import dispatch, multiply, add
from .units import lookup_unit, QSPACE

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
            raise EvalError(f"Unassigned variable: '{name}'")
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
        return make_quantity(child_values[0], node.value)
    raise EvalError(f"Unknown evaluation mode: '{mode}' (This is a bug!)")

def make_quantity(magnitude, unit_signature):
    if not is_number(magnitude):
        raise EvalError(f"Tried to add units to '{type(magnitude)}', which isn't a magnitude.")
    qv, multiple, offset = compose_units(unit_signature)
    return Quantity(add(
                        multiply(magnitude, number(multiple)),
                        number(offset)),
                    quantity_vector)

def compose_units(unit_sig):
    offset = 0
    multiple = 1
    qv = QSPACE.get_zero()
    unit_exp_inv_triplets = ([(name, exp, False) for name, exp in unit_sig.units]
        + [(name, exp, True) for name, exp in unit_sig.inverted_units])
    for name, exp, invert in unit_exp_pairs:
        unit = lookup_unit(name)
        if unit is None:
            raise EvalError(f"Unknown unit '{name}'. (Remember that it's case-sensitive).")
        if invert:
            exp = -exp
        qv *= unit.quantity_vector ** exp
        multiple *= unit.multiple ** exp
        offset = unit.offset
        if offset != 0 and len(unit_exp_pairs) > 1:
            raise EvalError(f"Can't combine unit '{name}' with other units, since it has an offset.")
        if offset != 0 and exp != 1:
            raise EvalError(f"Can't raise unit '{name}' to a power because it has an offset.")
    return qv, multiple, offset

