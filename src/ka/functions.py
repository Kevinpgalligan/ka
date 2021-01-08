import collections
import operator
import math

from .types import Number, Float, Integer, divide, coerce, number

FUNCTIONS = collections.defaultdict(list)

def dispatch(name, args):
    global FUNCTIONS
    if name not in FUNCTIONS:
        # TODO "did you mean...?" based on string distance.
        raise Exception("Unknown function " + name)
    for f, types in FUNCTIONS[name]:
        if len(types) == len(args) and all(isinstance(arg, t) for arg, t in zip(args, types)):
            return f(*args)
    # TODO list the signatures.
    raise Exception(f"Didn't match any signatures of '{name}'.")

def multiply(x, y):
    return dispatch("*", (x, y))

def register_function(f, name, arg_types):
    global FUNCTIONS
    FUNCTIONS[name].append((f, arg_types))

def register_binary_op(name, op):
    def new_op(n1, n2):
        n1, n2 = coerce(n1, n2)
        return number(op(n1.x, n2.x))
    register_function(new_op, name, (Number, Number))

def register_unary_op(name, op):
    def new_op(n):
        return number(op(n.x))
    register_function(new_op, name, (Number,))

def register_numeric_function(name, f, num_args=1):
    def new_f(*ns):
        return number(f(*[n.x for n in ns]))
    register_function(new_f, name, num_args*(Number,))

def choose(n, k):
    # Import inside the function since scipy is slow to load.
    # Will get rid of scipy dependency if possible.
    import scipy.special
    return number(scipy.special.comb(n.x, k.x, exact=True))

def factorial(n):
    import scipy.special
    return number(scipy.special.factorial(n.x, exact=True))

BINARY_OPS = [
    ("+", operator.add),
    ("-", operator.sub),
    ("*", operator.mul),
    ("/", divide),
    ("%", operator.mod),
    ("^", operator.pow)
]
for name, op in BINARY_OPS:
    register_binary_op(name, op)
register_unary_op("+", operator.pos)
register_unary_op("-", operator.neg)

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
    ("i", int),
    ("f", float)
]
for name, f in NUMERIC_FUNCTIONS:
    register_numeric_function(name, f)
register_numeric_function("log", lambda base, x: math.log(x, base), num_args=2)
register_function(choose, "C", (Integer, Integer))
register_function(factorial, "!", (Integer,))
