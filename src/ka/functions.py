import collections
import operator
import math
from numbers import Number, Integral
from fractions import Fraction as frac

from .types import simplify_type, Quantity, get_external_type_name
from .units import QSPACE

FUNCTIONS = collections.defaultdict(list)

class UnknownFunctionError(Exception):
    def __init__(self, name):
        self.name = name

class NoMatchingFunctionSignatureError(Exception):
    def __init__(self, name, attempted_signature, actual_signatures):
        self.name = name
        self.attempted_signature = attempted_signature
        self.actual_signatures = actual_signatures

class IncompatibleQuantitiesError(Exception):
    def __init__(self, qv1, qv2):
        self.qv1 = qv1
        self.qv2 = qv2

def dispatch(name, args):
    global FUNCTIONS
    if name not in FUNCTIONS:
        raise UnknownFunctionError(name)
    matching_signatures = lookup_function(name, args)
    if not matching_signatures:
        all_signatures = list(map(lambda x: x[1], FUNCTIONS[name]))
        all_sig_names = [tuple(map(lambda t: t.__name__, sig))
                         for sig in all_signatures]
        raise NoMatchingFunctionSignatureError(
            name,
            list(map(get_external_type_name, args)),
            all_sig_names)
    f = get_closest_match(matching_signatures)
    return simplify_type(f(*args))

def lookup_function(name, args):
    return [(f, types) for (f, types) in FUNCTIONS[name]
            if (len(types) == len(args)
                and all(isinstance(arg, t) for arg, t in zip(args, types)))]

def get_closest_match(matching_signatures):
    # (Integral, Integral) should come before
    # (Rational, Rational), for example. Unclear what
    # to do in case there's (Integral, Rational) and
    # (Rational, Integral).
    closest_f, closest_types = matching_signatures[0]
    for f, types in matching_signatures[1:]:
        if types_below(types, closest_types):
            closest_f, closest_types = f, types
    return closest_f

def types_below(types_A, types_B):
    # Returns whether types_A is clearly below types_B in
    # the type hierarchy.
    return all(issubclass(tA, tB) for tA, tB in zip(types_A, types_B))

def register_function(f, name, arg_types):
    global FUNCTIONS
    FUNCTIONS[name].append((f, arg_types))

def register_binary_op(name, op):
    register_function(op, name, (Number, Number))

def register_numeric_function(name, f, num_args=1):
    register_function(f, name, num_args*(Number,))
    if num_args == 1:
        def quantity_function(quantity):
            return Quantity(f(quantity.mag), quantity.qv)
        register_function(quantity_function, name, (Quantity,))

def choose(n, k):
    # Import inside the function since scipy is slow to load.
    # Will get rid of scipy dependency if possible.
    import scipy.special
    return scipy.special.comb(n, k, exact=True)

def factorial(n):
    import scipy.special
    return scipy.special.factorial(n, exact=True)

def fraction_divide(n1, n2):
    return frac(n1, n2)

BINARY_OPS = [
    ("+", operator.add),
    ("-", operator.sub),
    ("*", operator.mul),
    ("/", operator.truediv),
    ("%", operator.mod),
    ("^", operator.pow)
]
for name, op in BINARY_OPS:
    register_binary_op(name, op)
# Override division for integers so that
# it returns a fraction.
register_function(fraction_divide, "/", (Integral, Integral))

NUMERIC_FUNCTIONS = [
    ("sin", math.sin),
    ("cos", math.cos),
    ("tan", math.tan),
    ("sqrt", math.sqrt),
    ("ln", math.log),
    ("log10", math.log10),
    ("log2", math.log2),
    ("abs", abs),
    ("floor", math.floor),
    ("ceil", math.ceil),
    ("round", round),
    ("int", int),
    ("float", float),
    ("+", operator.pos),
    ("-", operator.neg)
]
for name, f in NUMERIC_FUNCTIONS:
    register_numeric_function(name, f)
register_numeric_function("log", lambda base, x: math.log(x, base), num_args=2)
register_function(choose, "C", (Integral, Integral))
register_function(factorial, "!", (Integral,))
def register_quantities_op(name, quantity_vector_combiner=None):
    def f(q1, q2):
        if quantity_vector_combiner is None:
            if q1.qv != q2.qv:
                raise IncompatibleQuantitiesError(q1.qv, q2.qv)
            new_qv = q1.qv
        else:
            new_qv = quantity_vector_combiner(q1.qv, q2.qv)
        # Use function dispatch to determine how to combine
        # the magnitudes.
        return Quantity(dispatch(name, (q1.mag, q2.mag)), new_qv)
    register_function(f, name, (Quantity, Quantity))
    # Now handle operations on numbers & quantities.
    def left_is_number(n, q):
        return f(Quantity(n, QSPACE.get_zero()), q)
    def right_is_number(q, n):
        return left_is_number(n, q)
    register_function(left_is_number, name, (Number, Quantity))
    register_function(right_is_number, name, (Quantity, Number))

register_quantities_op("+")
register_quantities_op("-")
register_quantities_op("*", lambda qv1, qv2: qv1*qv2)
register_quantities_op("/", lambda qv1, qv2: qv1/qv2)
