import collections
import operator
import math
from numbers import Number, Integral
from fractions import Fraction as frac

from .types import simplify_type, Quantity, get_external_type_name, Array
from .units import QSPACE
from .probability import (Binomial, Poisson, Geometric, Bernoulli,
                          UniformInt, Exponential, Uniform, Gaussian,
                          RandomVariable, Event, DoubleEvent, ComparisonOp,
                          DiscreteRandomVariable)
from .utils import choose, factorial
from functools import cmp_to_key

FUNCTIONS = collections.defaultdict(list)
FUNCTION_DOCUMENTATION = {}

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

class ExitKaSignal(Exception):
    pass

class FunctionArgError(Exception):
    def __init__(self, msg):
        self.msg = msg

def make_sig_printable(sig):
    return tuple(map(lambda t: t.__name__, sig))

def dispatch(name, args):
    global FUNCTIONS
    if name not in FUNCTIONS:
        raise UnknownFunctionError(name)
    matching_signatures = lookup_function(name, args)
    if not matching_signatures:
        all_signatures = list(map(lambda x: x[1], FUNCTIONS[name]))
        all_sig_names = [make_sig_printable(sig) for sig in all_signatures]
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

def register_function(f, name, arg_types, docstring=None):
    global FUNCTIONS
    FUNCTIONS[name].append((f, arg_types))
    if docstring is not None and name not in FUNCTION_DOCUMENTATION:
        FUNCTION_DOCUMENTATION[name] = docstring

def register_binary_op(name, op, docstring=None):
    register_function(op, name, (Number, Number), docstring=None)

def register_numeric_function(name, f, num_args=1, docstring=None):
    register_function(f, name, num_args*(Number,), docstring=docstring)
    if num_args == 1:
        def quantity_function(quantity):
            return Quantity(f(quantity.mag), quantity.qv)
        register_function(quantity_function, name, (Quantity,))

def fraction_divide(n1, n2):
    return frac(n1, n2)

def intify(f):
    def f_new(x, y):
        return 1 if f(x, y) else 0
    return f_new

BINARY_OPS = [
    ("+", operator.add, "Addition binary operator."),
    ("-", operator.sub, "Subtraction binary operator."),
    ("*", operator.mul, "Multiplication binary operator."),
    ("/", operator.truediv, "Division binary operator. Passing 2 integers results in a fraction."),
    ("%", operator.mod, "Modulo binary operator. 4%3=1."),
    ("^", operator.pow, "Exponentiation binary operator. 2^3=8."),
    ("<", intify(operator.lt), "Less than."),
    ("<=", intify(operator.le), "Less than or equal to."),
    ("==", intify(operator.eq), "Equals."),
    ("!=", intify(operator.ne), "Not equals."),
    (">", intify(operator.gt), "Greater than."),
    (">=", intify(operator.ge), "Greater than or equal to."),
]
for name, op, docstring in BINARY_OPS:
    register_binary_op(name, op, docstring=docstring)
# Override division for integers so that
# it returns a fraction.
register_function(fraction_divide, "/", (Integral, Integral))

NUMERIC_FUNCTIONS = [
    ("sin", math.sin, "Trigonometric sine function."),
    ("cos", math.cos, "Trigonometric cosine function."),
    ("tan", math.tan, "Trigonometric tangent function."),
    ("sqrt", math.sqrt, "Square root of a number."),
    ("ln", math.log, "Natural log, base e."),
    ("log10", math.log10, "Logarithm base 10."),
    ("log2", math.log2, "Logarithm base 2."),
    ("abs", abs, "Absolute value of a number."),
    ("floor", math.floor, "Rounds a number down to the next smallest integer."),
    ("ceil", math.ceil, "Rounds a number up to the next largest integer."),
    ("round", round, "Rounds a number to the nearest integer."),
    ("int", int, "Converts a number to the nearest integer between that number and zero."),
    ("float", float, "Force a number (such as a fraction) to its (imprecise) floating point representation."),
    ("+", operator.pos, "Positive sign; prefix operator."),
    ("-", operator.neg, "Negate a number; prefix operator."),
]
for name, f, docstring in NUMERIC_FUNCTIONS:
    register_numeric_function(name, f, docstring=docstring)
register_numeric_function("log", lambda base, x: math.log(x, base), num_args=2, docstring="Logarithm function. The first argument determines the base.")
register_function(choose, "C", (Integral, Integral), "Binomial coefficient function from combinatorics. It returns how many ways there are from a total of n items (first argument) to select k items (second argument).")
register_function(factorial, "!", (Integral,), "Factorial function, postfix operator. 3!=6.")
def register_quantities_op(name,
                           quantity_vector_combiner=None,
                           wrap_in_quantity=True):
    def f(q1, q2):
        if quantity_vector_combiner is None:
            if q1.qv != q2.qv:
                raise IncompatibleQuantitiesError(q1.qv, q2.qv)
            new_qv = q1.qv
        else:
            new_qv = quantity_vector_combiner(q1.qv, q2.qv)
        # Use function dispatch to determine how to combine
        # the magnitudes.
        new_mag = dispatch(name, (q1.mag, q2.mag))
        return Quantity(new_mag, new_qv) if wrap_in_quantity else new_mag
    register_function(f, name, (Quantity, Quantity))
    # Now handle operations on numbers & quantities.
    def left_is_number(n, q):
        return f(Quantity(n, QSPACE.get_zero()), q)
    def right_is_number(q, n):
        return left_is_number(n, q)
    register_function(left_is_number, name, (Number, Quantity))
    register_function(right_is_number, name, (Quantity, Number))

for op in ["+", "-"]:
    register_quantities_op(op)
for op in ["<", "<=", "!=", "==", ">", ">="]:
    register_quantities_op(op, wrap_in_quantity=False)
register_quantities_op("*", lambda qv1, qv2: qv1*qv2)
register_quantities_op("/", lambda qv1, qv2: qv1/qv2)

def ka_quit():
    raise ExitKaSignal()

register_function(ka_quit, "quit", tuple(), docstring="Exit the program.")

RVS = (
    (Binomial, (Integral, Number), 
     "Binomial random variable with n samples and probability p."),
    (Poisson, (Integral,), "Poisson random variable with shape mu."), 
    (Geometric, (Number,), "Geometric random variable with parameter p."),
    (Bernoulli, (Number,), "Bernoulli random variable with parameter p."),
    (UniformInt, (Integral, Integral),
     "Uniform random variable with integer values between lower bound and upper bound (inclusive)."),
    (Exponential, (Number,),
     "Exponential random variable with shape parameter."),
    (Uniform, (Number, Number), "Uniform random variable with values between lower and upper bound."),
    (Gaussian, (Number, Number),
     "Gaussian/normal random variable parameterised by mean and standard deviation.")
)
for rvname, args, doc in RVS:
    register_function(rvname, rvname.__name__, args, docstring=doc)

register_function(lambda rv: rv.mean(), "mean", (RandomVariable,), "Get the mean of a random variable.")
register_function(lambda rv: rv.mean(), "E", (RandomVariable,), "Expectation of a random variable.")
register_function(lambda rv: rv.sample(), "sample", (RandomVariable,), "Sample a value from a random distribution.")

def sample_multiple(rv, n):
    return Array([rv.sample() for _ in range(n)])
register_function(sample_multiple,
                  "sample",
                  (RandomVariable, Integral),
                  "Sample multiple values from a random distribution.")

register_function(lambda x, y: Event(ComparisonOp.EQ, x, y),
                  ComparisonOp.EQ,
                  (DiscreteRandomVariable, Integral),
                  "Comparison operator.")

def make_event_fun(op):
    def event_fun(x, y):
        return Event(op, x, y)
    return event_fun

def make_double_event_fun(op1, op2):
    def event_fun(x, y, z):
        return DoubleEvent(op1, op2, x, y, z)
    return event_fun

for op1 in [ComparisonOp.LEQ, ComparisonOp.LT]:
    for args in [(Number, RandomVariable), (RandomVariable, Number)]:
        # Can't use a lambda here because it doesn't have
        # proper lexical closure. Annoying Python.
        register_function(make_event_fun(op1),
                          op1,
                          args,
                          "Comparison operator.")
    for op2 in [ComparisonOp.LEQ, ComparisonOp.LT]:
        register_function(make_double_event_fun(op1, op2),
                          "_".join([op1, op2]),
                          (Number, RandomVariable, Number),
                          "Double comparison.")

for etype in [Event, DoubleEvent]:
    register_function(lambda event: event.probability(), "P", (etype,), "Evaluate the probability of an event.")

def array_prod(arr):
    result = 1
    for e in arr.contents:
        result = dispatch("*", (e, result))
    return result

def array_min(arr):
    if len(arr.contents) == 0:
        raise FunctionArgError("Tried to get minimum of empty array.")
    result = arr.contents[0]
    for e in arr.contents:
        if dispatch("<", (e, result)):
            result = e
    return result

# Lovely duplication here.
def array_max(arr):
    if len(arr.contents) == 0:
        raise FunctionArgError("Tried to get maximum of empty array.")
    result = arr.contents[0]
    for e in arr.contents:
        if dispatch("<", (result, e)):
            result = e
    return result

# Should really have some sorta "reduce"-like abstraction. But the
# error-handling behaviour is different between them.
def array_sum(arr):
    if len(arr.contents) == 0:
        return 0
    result = arr.contents[0]
    for i in range(1, len(arr.contents)):
        result = dispatch("+", (result, arr.contents[i]))
    return result

def array_size(arr):
    return len(arr.contents)

def array_mean(arr):
    if len(arr.contents) == 0:
        raise FunctionArgError("Tried to take mean of empty array.")
    return dispatch("/", (dispatch("sum", (arr,)), len(arr.contents)))

def ka_cmp(x, y):
    if dispatch("<", (x, y)):
        return -1
    if dispatch("==", (x, y)):
        return 0
    return 1

def array_median(arr):
    if len(arr.contents) == 0:
        raise FunctionArgError("Tried to take median of empty array.")
    arr_sorted = list(sorted(arr.contents, key=cmp_to_key(ka_cmp)))
    print(arr_sorted)
    if len(arr_sorted)%2 == 0:
        mid_i = len(arr_sorted) // 2
        return dispatch("/", (dispatch("+",
                                       (arr_sorted[mid_i-1],
                                        arr_sorted[mid_i])),
                              2))
    return arr_sorted[len(arr_sorted)//2]
    
register_function(array_prod, "prod", (Array,), "Product of the elements of an array.")
register_function(array_sum, "sum", (Array,), "Sum of the elements of an array.")
register_function(array_mean, "mean", (Array,), "Mean of the elements of an array.")
register_function(array_median, "median", (Array,), "Median of the elements of an array.")
register_function(array_size, "size", (Array,), "Number of elements in an array.")
register_function(array_max, "max", (Array,), "Maximum element of an array.")
register_function(array_min, "min", (Array,), "Minimum element of an array.")

register_function(lambda lo, hi: Array(list(range(lo, hi+1))),
                  "range",
                  (Integral, Integral),
                  "Returns an array of the integers lo, lo+1, ..., hi.")
def ka_range(lo, hi, step):
    if not dispatch("<=", (lo, hi)):
        raise FunctionArgError(f"Lower bound of range (was {lo}) must be less than or equal to upper bound (was {hi}).")
    result = []
    curr = lo
    while dispatch("<=", (curr, hi)):
        result.append(curr)
        curr = dispatch("+", (curr, step))
    return Array(result)

register_function(ka_range, "range", (Number, Number, Number),
                  "Generates array of all numbers between lower bound and upper bound with given step size.")
