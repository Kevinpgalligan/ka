import math
import numbers
from fractions import Fraction as frac

def get_external_type_name(x):
    t = type(x)
    if t is int:
        t = numbers.Integral
    elif t is float:
        t = numbers.Real
    return t.__name__

class Quantity:
    def __init__(self, mag, qv):
        self.mag = mag
        self.qv = qv

    def __eq__(self, other):
        return (isinstance(other, Quantity)
                and self.mag == other.mag
                and self.qv == other.qv)

    def __str__(self):
        return "Quantity(" + ", ".join([str(self.mag), str(self.qv)]) + ")"

    def __repr__(self):
        return str(self)

def is_number(x):
    return isinstance(x, numbers.Number)

def simplify_type(x):
    if isinstance(x, numbers.Number):
        return simplify_number(x)
    if isinstance(x, Quantity):
        return Quantity(simplify_number(x.mag), x.qv)
    return x

def simplify_number(x):
    if isinstance(x, float):
        fraction, whole = math.modf(x)
        if fraction == 0:
            # Go straight to integers. Converting floats
            # to rationals results in ugly-looking fractions
            # due to rounding issues.
            return int(whole)
    elif isinstance(x, frac) and x.numerator % x.denominator == 0:
        return x.numerator // x.denominator
    return x

def divide(x, y):
    # Assuming they've been converted to have
    # the same type.
    if isinstance(x, int):
        return frac(x, y)
    return x/y
