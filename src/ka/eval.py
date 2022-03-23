import math
from .types import Quantity, is_number, get_external_type_name
from .functions import dispatch
from .units import lookup_unit, QSPACE, InvalidPrefixError

CONSTANTS = {
    "e": math.e,
    "pi": math.pi
}

class EvalModes:
    LEAF = "leaf"
    VARIABLE = "variable"
    FUNCALL = "funcall"
    ASSIGNMENT = "assignment"
    STATEMENTS = "statements"
    QUANTITY = "quantity"
    CONVERT_UNIT = "convert-unit"

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

def eval_parse_tree(root, env=None):
    if env is None:
        env = EvalEnvironment()
    try:
        return eval_node(root, env)
    except ZeroDivisionError:
        raise EvalError("Attempted to divide by zero.")
    except OverflowError:
        raise EvalError("Overflow, numerical result out of range!")

def eval_node(node, env):
    return eval_based_on_mode(
        node,
        env,
        [eval_node(child, env) for child in node.children])

def eval_based_on_mode(node, env, child_values):
    mode = node.eval_mode
    if mode == EvalModes.LEAF:
        return node.value
    if mode == EvalModes.VARIABLE:
        return env.get_variable(node.value)
    if mode == EvalModes.FUNCALL:
        return dispatch(node.value, child_values)
    if mode == EvalModes.ASSIGNMENT:
        return env.set_variable(node.value, child_values[0])
    if mode == EvalModes.STATEMENTS:
        return child_values[-1] if child_values else None
    if mode == EvalModes.QUANTITY:
        return make_quantity(child_values[0], node.value)
    if mode == EvalModes.CONVERT_UNIT:
        return convert_quantity(child_values[0], node.value)
    raise EvalError(f"Unknown evaluation mode: '{mode}' (This is a bug!)")

def make_quantity(magnitude, unit_signature):
    if not is_number(magnitude):
        raise EvalError(f"Tried to add units on top of existing units. Only a magnitude can be tagged with units.")
    qv, multiple, offset = compose_units(unit_signature)
    return Quantity(multiple*magnitude + offset, qv)

def convert_quantity(quantity, unit_sig):
    qv, multiple, offset = compose_units(unit_sig)
    if not isinstance(quantity, Quantity):
        raise EvalError(f"Tried to change unit of {get_external_type_name(quantity)}, which doesn't have a unit in the first place.")
    if qv != quantity.qv:
        raise EvalError(
            f"Tried to convert quantity of type {quantity.qv.prettified()} to unit of incompatible type {qv.prettified()}.")
    # Basically, undo the conversion that you would do to initially go from
    # this unit to the standard unit of this quantity.
    return dispatch("/",
                    (dispatch("-", (quantity.mag, offset)),
                     multiple))

def compose_units(unit_sig):
    offset = 0
    multiple = 1
    qv = QSPACE.get_zero()
    unit_specs = ([(name, exp, False) for name, exp in unit_sig.units]
        + [(name, exp, True) for name, exp in unit_sig.inverted_units])
    for name, exp, invert in unit_specs:
        try:
            unit = lookup_unit(name)
        except InvalidPrefixError:
            raise EvalError(f"Can't apply a prefix to unit '{name}', as it has an offset!")
        if unit is None:
            raise EvalError(f"Unknown unit '{name}'. (Remember that it's case-sensitive).")
        if invert:
            exp = -exp
        qv *= unit.quantity_vector ** exp
        # Negative exponent turns the multiple into a float, even
        # if the multiplier is just 1 anyway. So avoid this annoyance
        # by only multiplying if the multiplier is NOT 1.
        if unit.multiple != 1:
            multiple *= unit.multiple ** exp
        offset = unit.offset
        if offset != 0 and len(unit_specs) > 1:
            raise EvalError(f"Can't combine unit '{name}' with other units, since it has an offset.")
        if offset != 0 and exp != 1:
            raise EvalError(f"The only valid exponent for unit '{name}' is 1, but it was given as {exp}.")
    return qv, multiple, offset

