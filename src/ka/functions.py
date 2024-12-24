import collections
import operator
import math
from numbers import Number, Integral, Rational
from fractions import Fraction as frac
import random

from .types import (simplify_type, Quantity, get_external_type_name,
    Array, Combinatoric, IntRange, fraction_divide, is_true,
    String, Bool, get_type_as_string, is_type, now, Instant,
    instant_plus_quantity, instant_plus_int, instant_minus_quantity,
    instant_minus_int, today, floor_instant, ceil_instant,
    instant_minus_instant, Interval, Any, KaRuntimeError,
    instant_lt, instant_leq, instant_gt, instant_geq,
    interval_get_upper, interval_get_lower, get_year, get_month,
    get_day, get_hour, get_minute, get_second, TypeAlias)
from .units import QSPACE
from .probability import (Binomial, Poisson, Geometric, Bernoulli,
                          UniformInt, Exponential, Uniform, Gaussian,
                          RandomVariable, Event, DoubleEvent, ComparisonOp,
                          DiscreteRandomVariable, unit)
from .utils import lazy_choose, lazy_factorial, _g, separate_kwargs
from .plot import (plot, line, check_all_numerical, Plot, PlotDrawing,
    only_not_none, vline, hline, scatter, text, options, get_plt)
from functools import cmp_to_key

FUNCTIONS = collections.defaultdict(list)
FUNCTION_DOCUMENTATION = {}

class FunctionSignature:
    def __init__(self, args, vararg=None, kw_args=None):
        self.args = args
        self.vararg = vararg
        self.kw_args = kw_args or dict()

    def matches(self, args):
        i = 0
        while i < len(self.args):
            if i >= len(args):
                return False
            t = self.args[i]
            if not is_type(args[i], t):
                return False
            i += 1
        return (i == len(args)
            or (self.vararg is not None
                and all(is_type(arg, self.vararg)
                        for arg in args)))

    def __str__(self):
        if (len(self.args) == 0
                and self.vararg is None
                and len(self.kw_args) == 0):
            return "...none..."
        return "".join([
            "(",
            ", ".join(map(get_type_as_string, self.args)),
            ", " if (len(self.args)>0) and self.vararg else "",
            "*" if self.vararg else "",
            get_type_as_string(self.vararg) if self.vararg else "",
            ", " if (len(self.args)>0 or self.vararg) and len(self.kw_args)>0 else "",
            ", ".join(f"{name}: {get_type_as_string(t)}"
                      for name, t in self.kw_args.items()),
            ")"
        ])

    def coerce_args(self, args):
        # Assumes that the args match the signature.
        result = []
        i = 0
        while i < len(self.args):
            result.append(coerce_to(args[i], self.args[i]))
            i += 1
        while i < len(args):
            # Must be vararg type.
            result.append(coerce_to(args[i], self.vararg))
            i += 1
        return result

    def coerce_kwarg(self, k, v):
        # Likewise.
        return coerce_to(v, self.kw_args[k])

class FunctionHeader:
    def __init__(self, name, f, sig):
        self.name = name
        self.f = f
        self.sig = sig

    def sig_matches(self, args):
        return self.sig.matches(args)

    def coerce_args(self, args):
        return self.sig.coerce_args(args)

    def coerce_kwarg(self, k, v):
        return self.sig.coerce_kwarg(k, v)

    def __str__(self):
        return f"FunctionHeader[name='{self.name}', f={self.f}, sig={self.sig}]"

    def __repr__(self):
        return str(self)

class UnknownFunctionError(Exception):
    def __init__(self, name):
        self.name = name

class UnknownKeywordError(Exception):
    def __init__(self, fn_header, kw_name):
        self.fn_header = fn_header
        self.kw_name = kw_name

class BadTypeKeywordError(Exception):
    def __init__(self, fn_header, kw_name, kw_value, expected_type):
        self.fn_header = fn_header
        self.kw_name = kw_name
        self.kw_value = kw_value
        self.expected_type = expected_type

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
    return str(sig)

def dispatch(name, args, kw_args=None):
    global FUNCTIONS
    if kw_args is None:
        kw_args = dict()
    if name not in FUNCTIONS:
        raise UnknownFunctionError(name)
    matching_headers = lookup_function(name, args)
    if not matching_headers:
        all_signatures = list(map(lambda x: x.sig, FUNCTIONS[name]))
        all_sig_names = [str(sig) for sig in all_signatures]
        raise NoMatchingFunctionSignatureError(
            name,
            list(map(get_external_type_name, args)),
            all_sig_names)
    header = get_closest_match(matching_headers)
    for k, v in kw_args.items():
        expected_type = header.sig.kw_args.get(k, None)
        if expected_type is None:
            raise UnknownKeywordError(header, k)
        if not is_type(v, expected_type):
            raise BadTypeKeywordError(header, k, v, expected_type)
    return simplify_type(
        header.f(*header.coerce_args(args),
                 **dict((k, header.coerce_kwarg(k, v))
                        for k, v in kw_args.items())))

def lookup_function(name, args):
    return [header for header in FUNCTIONS[name]
            if header.sig_matches(args)]

def get_closest_match(matching_headers):
    # (Integral, Integral) should come before
    # (Rational, Rational), for example. Unclear what
    # to do in case there's (Integral, Rational) and
    # (Rational, Integral).
    closest_header = matching_headers[0]
    for header in matching_headers[1:]:
        if types_below(header.sig, closest_header.sig):
            closest_header = header
    return closest_header

def types_below(sig_A, sig_B):
    # Returns whether the types in sig_A are clearly below the types
    # in sig_B in the type hierarchy.
    return all(type_below(tA, tB)
               for tA, tB in zip(sig_A.args, sig_B.args))

def type_below(t1, t2):
    if isinstance(t1, TypeAlias): t1 = t1.actual_type
    if isinstance(t2, TypeAlias): t2 = t2.actual_type
    return issubclass(t1, t2)

def register_function(f, name, arg_types,
        docstring=None,
        kw_args=None,
        vararg_type=None):
    """kwargs should be a mapping from names to types."""
    global FUNCTIONS
    FUNCTIONS[name].append(
        FunctionHeader(name,
                       f,
                       FunctionSignature(arg_types,
                                         vararg=vararg_type,
                                         kw_args=kw_args)))
    if docstring is not None and name not in FUNCTION_DOCUMENTATION:
        FUNCTION_DOCUMENTATION[name] = docstring

def register_binary_op(name, op, docstring=None):
    register_function(op, name, (Number, Number), docstring=docstring)

def register_commutative_op(f, name, type1, type2):
    def reverse_f(y, x):
        return f(x, y)
    register_function(f, name, (type1, type2))
    register_function(reverse_f, name, (type2, type1))

def register_numeric_function(name, f, num_args=1, docstring=None):
    register_function(f, name, num_args*(Number,), docstring=docstring)
    if num_args == 1:
        def quantity_function(quantity):
            return Quantity(f(quantity.mag), quantity.qv)
        register_function(quantity_function, name, (Quantity,))

def intify(f):
    def f_new(x, y):
        return 1 if f(x, y) else 0
    return f_new

def resolve_combinatoric(co):
    return co.resolve()

def coerce_to(x, t):
    # Converts value x to type t, assuming that it's a valid conversion.
    if isinstance(x, Combinatoric) and t == Number:
        return resolve_combinatoric(x)
    return x

def is_fractional(x):
    return not is_true(dispatch("==", (dispatch("int", (x,)), x)))

def strict_pow(x, y):
    # Fractional power, and negative number.
    if is_fractional(y) and is_true(dispatch("<", (x, 0))):
        raise KaRuntimeError("Tried to take fractional power of a negative number.")
    return x**y

BINARY_OPS = [
    ("+", operator.add, "Addition binary operator."),
    ("-", operator.sub, "Subtraction binary operator."),
    ("*", operator.mul, "Multiplication binary operator."),
    ("/", operator.truediv, "Division binary operator. Passing 2 integers results in a fraction."),
    ("%", operator.mod, "Modulo binary operator. 4%3=1."),
    ("^", strict_pow, "Exponentiation binary operator. 2^3=8."),
    ("<", intify(operator.lt), "Less than."),
    ("<=", intify(operator.le), "Less than or equal to."),
    ("==", intify(operator.eq), "Equals."),
    ("!=", intify(operator.ne), "Not equals."),
    (">", intify(operator.gt), "Greater than."),
    (">=", intify(operator.ge), "Greater than or equal to."),
]
for name, op, docstring in BINARY_OPS:
    register_binary_op(name, op, docstring=docstring)
# This ensures that, if isn't a more specific equals operator to compare two
# items, then they'll be considered unequal.
register_function(lambda x, y: 0, "==", (Any, Any))
register_function(lambda x, y: 1, "!=", (Any, Any))
# Override division for integers so that
# it returns a fraction.
register_function(fraction_divide, "/", (Integral, Integral))
# But we want special case for combinatoric times combinatoric, or
# combinatoric times integer/fraction.
def comb_times_comb(c1, c2):
    return c1.mul(c2.ns, c2.ds)
def comb_div_comb(c1, c2):
    return c1.mul(c2.ds, c2.ns)
def comb_times_frac(c, f):
    n, d = get_ratio(f)
    return c.mul([] if n == 1 else [IntRange(n, n)],
                 [] if d == 1 else [IntRange(d, d)])
def get_ratio(f):
    if isinstance(f, int):
        return (f, 1)
    return f.as_integer_ratio()
def comb_div_frac(c, f):
    return comb_times_frac(c, 1/f)
def frac_times_comb(f, c):
    return comb_times_frac(c, f)
def frac_div_comb(f, c):
    return comb_times_frac(Combinatoric(ns=c.ds, ds=c.ns), f)
register_function(comb_times_comb, "*", (Combinatoric, Combinatoric))
register_function(comb_div_comb, "/", (Combinatoric, Combinatoric))
register_function(comb_times_frac, "*", (Combinatoric, Rational))
register_function(comb_div_frac, "/", (Combinatoric, Rational))
register_function(frac_times_comb, "*", (Rational, Combinatoric))
register_function(frac_div_comb, "/", (Rational, Combinatoric))

def ka_ln(x): return ka_log(x, math.e)
def ka_log10(x): return ka_log(x, 10)
def ka_log2(x): return ka_log(x, 2)

def ka_log(x, base):
    if dispatch("<=", (x, 0)):
        raise KaRuntimeError(f"Non-positive value passed to log: {x}")
    return math.log(x, base)

def ka_sqrt(x):
    if dispatch("<", (x, 0)):
        raise KaRuntimeError(f"Negative value passed to sqrt: {x}")
    return math.sqrt(x)

NUMERIC_FUNCTIONS = [
    ("sin", math.sin, "Trigonometric sine function."),
    ("cos", math.cos, "Trigonometric cosine function."),
    ("tan", math.tan, "Trigonometric tangent function."),
    ("sqrt", ka_sqrt, "Square root of a number."),
    ("ln", ka_ln, "Natural log, base e."),
    ("log10", ka_log10, "Logarithm base 10."),
    ("log2", ka_log2, "Logarithm base 2."),
    ("abs", abs, "Absolute value of a number."),
    ("floor", math.floor, "Rounds a number down to the next smallest integer."),
    ("ceil", math.ceil, "Rounds a number up to the next largest integer."),
    ("round", round, "Rounds a number to the nearest integer."),
    ("int", int, "Converts a number to the nearest integer in the direction of zero."),
    ("float", float, "Force a number (such as a fraction) to its (imprecise) floating point representation."),
    ("+", operator.pos, None),
    ("-", operator.neg, None),
]
for name, f, docstring in NUMERIC_FUNCTIONS:
    register_numeric_function(name, f, docstring=docstring)
register_numeric_function("log",
                          ka_log,
                          num_args=2,
                          docstring="Logarithm function. The first argument determines the base.")

def max_vararg(*args):
    return max(*args)
def min_vararg(*args):
    return min(*args)
register_function(max_vararg, "max", tuple(), vararg_type=Number)
register_function(min_vararg, "min", tuple(), vararg_type=Number)

register_function(lazy_choose,
                  "C",
                  (Integral, Integral),
                  "Binomial coefficient function from combinatorics. It returns how many ways there are to select k items (second argument) from a total of n items (first argument).")
register_function(lazy_factorial,
                  "!",
                  (Integral,),
                  "Factorial postfix operator.")
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

##############
# Randomness #
##############
register_function(
    unit, "rand", tuple(),
    docstring="Random float value between 0-1")
register_function(
    random.seed, "seed", (Integral,),
    docstring="Sets seed for random number generation, sampling, etc.")

###############
# Probability #
###############
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
                          "Double comparison operator.")

for etype in [Event, DoubleEvent]:
    register_function(lambda event: event.probability(), "P", (etype,), "Evaluate the probability of an event.")

##########
# Arrays #
##########
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

def in_array(x, arr):
    return any(dispatch("==", (x, e)) for e in arr)

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
register_function(array_max, "max", (Array,), "Maximum of a selection of numbers.")
register_function(array_min, "min", (Array,), "Minimum of a selection of numbers.")
register_function(in_array, "in", (Any, Array), "Whether an element is present in a set/array.")

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
                  "Generates array of all numbers between lower bound (1st arg) and upper bound (2nd arg) with given step size (3rd arg).")

############
# Plotting #
############
# Had to move this here so it could use `dispatch` without a circular
# dependency.
def histogram(xs, **kwargs):
    check_all_numerical(xs)
    sel, o = separate_kwargs(kwargs,
        ["label", "cumulative", "normalise", "colour",
         "num_bins", "bin_width", "start", "align", "border_colour"])
    start = _g(sel, "start", 0)
    bin_width = _g(sel, "bin_width")
    num_bins = _g(sel, "num_bins", 10)
    def do():
        nonlocal start
        if num_bins <= 0:
            raise KaRuntimeError("Number of bins  must be positive but was " + str(num_bins))
        if bin_width:
            if bin_width <= 0:
                raise KaRuntimeError("Bin width must be positive but was " + str(bin_width))
            lo = dispatch("min", (xs,))
            if dispatch("<", (lo, start)):
                start -= bin_width*math.ceil(dispatch("-", (start, lo))/bin_width)
            hi = dispatch("max", (xs,))
            bins = []
            b = start
            while True:
                if b > hi:
                    break
                bins.append(b)
                b += bin_width
        else:
            bins = num_bins
        normalise = _g(sel, "normalise", False)
        params = dict(
            label=_g(sel, "label"),
            color=_g(sel, "colour"),
            cumulative=is_true(_g(sel, "cumulative", False)),
            density=is_true(normalise),
            # Don't pass unless necessary.
            stacked=True if is_true(normalise) else None,
            align=_g(sel, "align", "mid"),
            bins=bins,
            edgecolor=_g(sel, "border_colour"))
        get_plt().hist(xs, **only_not_none(params))
    return PlotDrawing(do, o)

plot_option_types = dict(
    xlabel=String,
    ylabel=String,
    xlo=Number,
    xhi=Number,
    ylo=Number,
    yhi=Number,
    grid=Bool,
    title=String,
    ylog=Bool,
    xlog=Bool,
    legend=Bool,
    xticks=Array,
    yticks=Array,
    integer_x_ticks=Bool,
    integer_y_ticks=Bool)

register_function(options, "options", tuple(), "Configuring plot options.",
                  plot_option_types)

register_function(
    line,
    "line",
    (Array, Array),
    "A 2-dimensional line plot.",
    dict(
        label=String,
        marker=String,
        markercolour=String,
        colour=String,
        **plot_option_types))

register_function(
    histogram,
    "histogram",
    (Array,),
    "A histogram in the form of a bar chart.",
    dict(
        label=String,
        cumulative=Bool,
        normalise=Bool,
        colour=String,
        num_bins=Number,
        bin_width=Number,
        start=Number,
        align=String,
        border_colour=String,
        **plot_option_types))

register_function(plot,
    "plot",
    tuple(),
    "Plots a series of plottable things.",
    vararg_type=Plot)

register_function(
    scatter,
    "scatter",
    (Array, Array),
    "Scatter plot of 2d data.",
    dict(
        label=String,
        marker=String,
        size=Number,
        colour=String,
        **plot_option_types))

register_function(vline, "vline", (Number,),
                  "Draw a vertical line at the given x coordinate.",
                  kw_args=dict(colour=String, weight=Number, style=String))
register_function(hline, "hline", (Number,),
                  "Draw a horizontal line at the given y coordinate.",
                  kw_args=dict(colour=String, weight=Number, style=String))
register_function(text, "text", (Number, Number, String),
                  "Write text with top-left corner at the given x & y coordinate.",
                  kw_args=dict(colour=String, size=Number))

#################
# Dates & times #
#################
register_function(
    now, "now", tuple(),
    "Returns an Instant representing the current time in the local timezone.")

register_function(
    today, "today", tuple(),
    "Returns an Instant representing the start of the current day.")

register_function(floor_instant, "floor", (Instant,))
register_function(ceil_instant, "ceil", (Instant,))

register_function(instant_minus_instant, "-", (Instant, Instant))
register_commutative_op(instant_plus_quantity, "+", Instant, Quantity)
register_commutative_op(instant_plus_int, "+", Instant, Integral)
register_function(instant_minus_quantity, "-", (Instant, Quantity))
register_function(instant_minus_int, "-", (Instant, Integral))

register_function(operator.eq, "==", (Instant, Instant))
register_function(operator.ne, "!=", (Instant, Instant))
register_function(instant_lt, "<", (Instant, Instant))
register_function(instant_leq, "<=", (Instant, Instant))
register_function(instant_gt, ">", (Instant, Instant))
register_function(instant_geq, ">=", (Instant, Instant))

register_function(get_year, "year", (Instant,))
register_function(get_month, "month", (Instant,))
register_function(get_day, "day", (Instant,))
register_function(get_hour, "hour", (Instant,))
register_function(get_minute, "minute", (Instant,))
register_function(get_second, "second", (Instant,))

#############
# Intervals #
#############
def make_interval_with_num_op(opname):
    def op(intr, n):
        new_a = dispatch(opname, (intr.a, n))
        new_b = dispatch(opname, (intr.b, n))
        return make_interval_from_bounds(new_a, new_b)
    return op

def make_num_with_interval_op(opname):
    def op(intr, n):
        new_a = dispatch(opname, (n, intr.a))
        new_b = dispatch(opname, (n, intr.b))
        return make_interval_from_bounds(new_a, new_b)
    return op

def make_interval_from_bounds(x, y):
    return Interval(dispatch("min", (x, y)),
                    dispatch("max", (x, y)))

for n in ["+", "*"]:
    register_commutative_op(make_interval_with_num_op(n), n, Interval, Number)
for n in ["-", "/"]:
    register_function(make_interval_with_num_op(n), n, (Interval, Number))

def make_interval(a, b):
    if not dispatch("<=", (a, b)):
        return Interval(0, 0)
    return Interval(a, b)
register_function(make_interval, "interval", (Number, Number),
    docstring="Creates an interval within the given bounds.")

def interval_contains(intr, x):
    return dispatch("<=", (intr.a, x)) * dispatch("<=", (x, intr.b))
register_function(interval_contains, "contains", (Interval, Number),
    docstring="Whether an interval contains the given number.")

def interval_has_negative(intr):
    return dispatch("<", (intr.a, 0))

def interval_to_power(intr, exponent):
    if interval_has_negative(intr) and is_fractional(exponent):
        raise KaRuntimeError("Tried to raise an interval containing negative numbers to a fractional power.")
    candidates = [intr.a, intr.b]
    if interval_contains(intr, 0):
        if dispatch("<", (exponent, 0)):
            raise KaRuntimeError("Tried to raise interval to negative power when it contains zero.")
        candidates.append(0)
    args = tuple(dispatch("^", (x, exponent)) for x in candidates)
    return Interval(dispatch("min", args), dispatch("max", args))
register_function(interval_to_power, "^", (Interval, Number))

register_function(lambda x: x, "+", (Interval,))
def interval_flip(intr):
    return Interval(dispatch("-", (intr.b,)), dispatch("-", (intr.a,)))
register_function(interval_flip, "-", (Interval,))

def interval_sqrt(intr):
    if interval_has_negative(intr):
        raise KaRuntimeError(f"Tried to take square root of interval with negative numbers: {intr}")
    return Interval(dispatch("sqrt", (intr.a,)), dispatch("sqrt", (intr.b,)))
register_function(interval_sqrt, "sqrt", (Interval,))

def interval_ln(intr):
    return interval_log(intr, math.e)
def interval_log10(intr):
    return interval_log(intr, 10)
def interval_log2(intr):
    return interval_log(intr, 2)
def interval_log(intr, base):
    if dispatch("<=", (base, 0)):
        raise KaRuntimeError(f"Tried to take log with non-positive base: {base}")
    if dispatch("<=", (intr.a, 0)):
        raise KaRuntimeError(f"Tried to take log of interval containing non-positive numbers: {intr}")
    return Interval(dispatch("log", (intr.a, base)),
                    dispatch("log", (intr.b, base)))
register_function(interval_ln, "ln", (Interval,))
register_function(interval_log10, "log10", (Interval,))
register_function(interval_log2, "log2", (Interval,))
register_function(interval_log, "log", (Interval, Number))

def interval_abs(intr):
    vs = tuple(dispatch("abs", (x,)) for x in (intr.a, intr.b))
    return Interval(
        0 if interval_contains(intr, 0) else dispatch("min", vs),
        dispatch("max", vs))
register_function(interval_abs, "abs", (Interval,))

def register_interval_cmp(name, reverse_name):
    def swap(f):
        def swapped_f(y, x):
            return f(x, y)
        return swapped_f
    def interval_num(intr, x):
        return dispatch(name, (intr.b, x))
    def num_interval(x, intr):
        return dispatch(name, (x, intr.a))
    def interval_interval(I1, I2):
        return dispatch(name, (I1.b, I2.a))
    # This is a brainmelter, but wanted to avoid duplication.
    register_function(interval_num, name, (Interval, Number))
    register_function(swap(num_interval), reverse_name, (Interval, Number))
    register_function(num_interval, name, (Number, Interval))
    register_function(swap(interval_num), reverse_name, (Number, Interval))
    register_function(interval_interval, name, (Interval, Interval))
    register_function(swap(interval_interval), reverse_name, (Interval, Interval))
register_interval_cmp("<", ">")
register_interval_cmp("<=", ">=")

def in_interval(x, intr):
    return dispatch("<=", (intr.a, x)) * dispatch("<=", (x, intr.b))
register_function(in_interval, "in", (Number, Interval))

def interval_eq(I1, I2):
    return dispatch("==", (I1.a, I2.a)) * dispatch("==", (I1.b, I2.b))
register_function(interval_eq, "==", (Interval, Interval))

register_function(interval_get_lower, "lower", (Interval,),
                  "Get the lower bound of an interval.")
register_function(interval_get_upper, "upper", (Interval,),
                  "Get the upper bound of an interval.")

def interval_min(I, x):
    if dispatch("<=", (I.b, x)):
        return I
    if dispatch("<=", (x, I.a)):
        return Interval(x, x)
    return Interval(I.a, x)

def interval_max(I, x):
    if dispatch("<=", (I.b, x)):
        return Interval(x, x)
    if dispatch("<=", (x, I.a)):
        return I
    return Interval(x, I.b)

register_commutative_op(interval_min, "min", Interval, Number)
register_commutative_op(interval_max, "max", Interval, Number)

def interval_size(I):
    return dispatch("abs", (dispatch("-", (I.b, I.a)),))
register_function(interval_size, "size", (Interval,))

def interval_plusminus(x, y):
    return make_interval_from_bounds(dispatch("-", (x, y)), dispatch("+", (x, y)))

register_function(interval_plusminus, "±", (Number, Number))
register_function(interval_plusminus, "tol", (Number, Number))

FUNCTION_NAMES = list(FUNCTIONS.keys())

if __name__ == "__main__":
    print(resolve_combinatoric(
        Combinatoric(ns=[IntRange(2,9), IntRange(4,5)],
                     ds=[IntRange(3,7), IntRange(5,6)])))
    print(dispatch("sin", (Combinatoric(ns=[IntRange(1,3)]),)))
    print(repr(str(FunctionSignature(tuple(), vararg=Plot))))
    print(dispatch("now", tuple()))
    print(dispatch("^", (Interval(-2, 2), 2)))
