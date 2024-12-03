import math
from .types import Quantity, is_number, get_external_type_name, Array
from .functions import dispatch
from .units import lookup_unit, QSPACE, InvalidPrefixError
from .probability import ComparisonOp

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
    ARRAY = "array"
    ARRAY_WITH_CONDITION = "array-with-condition"
    KEYWORD_ARG = "keyword-arg"

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
        [eval_node(child, env) if node.eval_children else None
         for child in node.children])

def eval_based_on_mode(node, env, child_values):
    mode = node.eval_mode
    if mode == EvalModes.LEAF:
        return node.value
    if mode == EvalModes.VARIABLE:
        return env.get_variable(node.value)
    if mode == EvalModes.FUNCALL:
        return eval_funcall(node, child_values)
    if mode == EvalModes.ASSIGNMENT:
        return env.set_variable(node.value, child_values[0])
    if mode == EvalModes.STATEMENTS:
        return child_values[-1] if child_values else None
    if mode == EvalModes.QUANTITY:
        return make_quantity(child_values[0], node.value)
    if mode == EvalModes.CONVERT_UNIT:
        return convert_quantity(child_values[0], node.value)
    if mode == EvalModes.ARRAY:
        return Array(child_values)
    if mode == EvalModes.ARRAY_WITH_CONDITION:
        return eval_comprehension(node, env)
    if mode == EvalModes.KEYWORD_ARG:
        return child_values[0]
    raise EvalError(f"Unknown evaluation mode: '{mode}' (This is a bug!)")

def eval_funcall(node, child_values):
    num_pos_args = sum(1 for child in node.children
                         if child.eval_mode != EvalModes.KEYWORD_ARG)
    return dispatch(
        node.value,
        child_values[:num_pos_args],
        kw_args=dict((child.label, v)
                     for child, v
                     in zip(node.children[num_pos_args:],
                            child_values[num_pos_args:])))

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

def compare(operands, ops):
    return dispatch(get_comparison_fun(ops), operands)

def get_comparison_fun(ops):
    names = []
    for op in ops:
        if op == ComparisonOp.LEQ:
            names.append("<=")
        elif op == ComparisonOp.LT:
            names.append("<")
        else:
            names.append("=")
    return "_".join(names)

def eval_comprehension(node, env):
    num_assignments = node.meta["num_assignments"]
    num_conditions = len(node.children)-num_assignments-1
    if num_assignments == 0:
        raise EvalError("Complex array expression must introduce at least 1 variable.")
    body_node = node.children[0]
    assignment_nodes = [node.children[i] for i in range(1, 1+num_assignments)]
    assign_names = [child.meta["name"] for child in assignment_nodes]
    subarrays = [eval_node(assign_node, env) for assign_node in assignment_nodes]
    if any(not isinstance(subarray, Array) for subarray in subarrays):
        raise EvalError("Expected an array for variable assignment in complex array subclause.")
    condition_nodes = [node.children[i] for i in range(1+num_assignments, len(node.children))]
    subarray_index = 0
    output = Array([])
    while True:
        subarrays_exhausted = False
        for name, subarray in zip(assign_names, subarrays):
            if subarray_index >= len(subarray):
                subarrays_exhausted = True
                break
            env.set_variable(name, subarray[subarray_index])
        if subarrays_exhausted:
            break
        success = True
        for condition in condition_nodes:
            result = eval_node(condition, env)
            if not bool_like(result):
                raise EvalError("Expected boolean-interpretable result in array condition.")
            if result == 0:
                success = False
        if success:
            output.append(eval_node(body_node, env))
        subarray_index += 1
    return output

def bool_like(x):
    return x == 1 or x == 0

