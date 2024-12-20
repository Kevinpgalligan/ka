import math
import numbers
from fractions import Fraction as frac
from numbers import Number

class KaRuntimeError(Exception):
    def __init__(self, msg):
        self.msg = msg

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

def fraction_divide(n1, n2):
    return frac(n1, n2)

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

class Array:
    def __init__(self, contents):
        self.contents = contents

    def __eq__(self, other):
        return self.contents == other.contents

    def __str__(self):
        return str(self.contents)

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.contents)

    def __getitem__(self, i):
        return self.contents[i]

    def __contains__(self, x):
        return x in self.contents

    def append(self, x):
        self.contents.append(x)

class IntRange:
    def __init__(self, lo, hi):
        self.lo = lo
        self.hi = hi

    def copy(self):
        return IntRange(self.lo, self.hi)

    def is_empty(self):
        return self.lo > self.hi

    def intersects(self, other):
        return not (self.hi < other.lo or other.hi < self.lo)

    def difference(self, other):
        if self.hi < other.lo or other.hi < self.lo:
            return [self], [other]
        self_remain = []
        other_remain = []
        if self.lo <= other.lo and other.hi <= self.hi:
            return (
                ([IntRange(self.lo, other.lo-1)]
                 if self.lo < other.lo else [])
                + ([IntRange(other.hi+1, self.hi)]
                   if other.hi < self.hi else []),
                []
            )
        elif other.lo <= self.lo and self.hi <= other.hi:
            return (
                [],
                ([IntRange(other.lo, self.lo-1)]
                 if other.lo < self.lo else [])
                + ([IntRange(self.hi+1, other.hi)]
                   if self.hi < other.hi else [])
            )
        elif other.lo <= self.hi:
            return [IntRange(self.lo, other.lo-1)], [IntRange(self.hi+1, other.hi)]
        return [IntRange(self.lo, other.lo-1)], [IntRange(self.hi+1, other.hi)]

    def __str__(self):
        return f"[{self.lo},{self.hi}]"

class Combinatoric(numbers.Number):
    def __init__(self, ns=None, ds=None):
        # numerator IntRanges
        self.ns = ns if ns else []
        # denominator IntRanges
        self.ds = ds if ds else []
        self.value = None

    def mul(self, new_ns, new_ds):
        result_ds = []
        ns = self.ns + new_ns
        ds = self.ds + new_ds
        while ds:
            d = ds.pop()
            i = 0
            intersected = False
            while i < len(ns):
                if ns[i].intersects(d):
                    remaining_n, remaining_d = ns[i].difference(d)
                    ns = ns[:i] + remaining_n + ns[i+1:]
                    ds.extend(remaining_d)
                    intersected = True
                    break
                i += 1
            if not intersected:
                result_ds.append(d)
        return Combinatoric(ns=ns, ds=result_ds)

    def resolve(self):
        if self.value:
            return self.value
        result = 1
        # Copy all the ranges so that we don't corrupt the combinatoric.
        # Could probably avoid copying and still not corrupt, if this is slow.
        denom_ranges = [r.copy() for r in self.ds]
        for numerator_range in self.ns:
            numerator_range = numerator_range.copy()
            while not numerator_range.is_empty():
                # Multiply by the highest number in the range, since it's
                # likely to have the most divisors.
                result *= numerator_range.hi
                numerator_range.hi -= 1
                # Similarly, try to divide by the smallest number in the denominator
                # range, since it's most likely to divide evenly.
                # (Dividing to try keeping the result small).
                if denom_ranges and result % denom_ranges[-1].lo == 0:
                    result //= denom_ranges[-1].lo
                    denom_ranges[-1].lo += 1
                    if denom_ranges[-1].is_empty():
                        denom_ranges.pop()
        denom = 1
        for denom_range in denom_ranges:
            while not denom_range.is_empty():
                denom *= denom_range.lo
                denom_range.lo += 1
        
        self.value = simplify_type(fraction_divide(result, denom))
        return self.value

    def __eq__(self, other):
        return other == self.resolve()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "".join(["Combinatoric{",
            " ".join(map(str, self.ns)),
            ";",
            " ".join(map(str, self.ds)),
            "}"
        ])

class TypeAlias:
    def __init__(self, name, actual_type):
        self.name = name
        self.actual_type = actual_type

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

String = TypeAlias("String", str)
Bool = TypeAlias("Bool", Number)

def is_type(x, t):
    if isinstance(t, TypeAlias):
        t = t.actual_type
    return isinstance(x, t)

def is_true(x):
    return x != 0

def get_type_as_string(t):
    if isinstance(t, TypeAlias):
        return t.name
    return t.__name__

def get_external_type_name(x):
    t = type(x)
    if t is int:
        t = numbers.Integral
    elif t is float:
        t = numbers.Real
    elif isinstance(t, str):
        t = String
    return get_type_as_string(t)

if __name__ == "__main__":
    print(Combinatoric(ns=[IntRange(2, 9)]).mul(
        [IntRange(4, 5)],
        [IntRange(3, 7)]))
