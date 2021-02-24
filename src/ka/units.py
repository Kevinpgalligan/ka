from .functions import multiply

import collections
from fractions import Fraction as frac

QUANTITY_TO_QV = {}
QV_TO_QUANTITY = collections.defaultdict(list)
NAME_TO_UNIT = {}
SYMBOL_TO_UNIT = {}

class Vector:
    def __init__(self, xs):
        assert isinstance(xs, tuple)
        self.xs = xs

    def __len__(self):
        return len(self.xs)

    def __eq__(self, other):
        return isinstance(other, Vector) and all(x==y for x, y in zip(self.xs, other.xs))

    def __add__(self, other):
        return Vector(tuple(x+y for x, y in zip(self.xs, other.xs)))

    def __rmul__(self, a):
        return self.__mul__(a)

    def __mul__(self, a):
        return Vector(tuple(a*x for x in self.xs))

    def __neg__(self):
        return Vector(tuple(-x for x in self.xs))

    def __str__(self):
        return "<" + ",".join(str(x) for x in self.xs) + ">"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.xs)

    def __eq__(self, other):
        return isinstance(other, Vector) and self.xs == other.xs

    def __iter__(self):
        return iter(self.xs)

class QuantityVector:
    def __init__(self, v, names):
        self.v = v
        # Store the name of each dimension so that it can be
        # pretty-printed. And don't need to store a reference
        # to the space that this vector comes from.
        self.names = names

    def __mul__(self, other):
        return QuantityVector(self.v + other.v, self.names)

    def __pow__(self, a):
        return QuantityVector(a*self.v, self.names)

    def __div__(self, other):
        return self * QuantityVector(-other.v, other.names)

    def __eq__(self, other):
        return isinstance(other, QuantityVector) and self.v == other.v

    def __hash__(self):
        return hash(self.v)

    def prettified(self):
        return " ".join(f"{name}^{exp}" if exp != 1 else name
                        for exp, name in zip(self.v, self.names)
                        if exp!=0)

class QuantitySpace:
    def __init__(self, base_units):
        self.base_units = base_units
    
    def get_basis_vector(self, basis_name):
        assert basis_name in self.base_units
        return QuantityVector(
            Vector(tuple(1 if name==basis_name else 0 for name in self.base_units)),
            self.base_units)

class Unit:
    def __init__(self, symbol, singular_name, plural_name, quantities,
                 quantity_vector, multiple, offset):
        self.symbol = symbol
        self.singular_name = singular_name
        self.plural_name = plural_name
        self.quantities = quantities
        self.quantity_vector = quantity_vector
        self.multiple = multiple
        self.offset = offset

def register_unit(symbol,
                  singular_name,
                  quantities,
                  quantity_vector,
                  plural_name=None,
                  multiple=1,
                  offset=0):
    if plural_name is None:
        plural_name = singular_name + "s"
    if isinstance(quantities, str):
        quantities = [quantities]

    unit = Unit(symbol, singular_name, plural_name, quantities,
                quantity_vector, multiple, offset)

    global QUANTITY_TO_QV, QV_TO_QUANTITY, NAME_TO_UNIT, SYMBOL_TO_UNIT
    for q in quantities:
        if q in QUANTITY_TO_QV:
            # Each quantity name can be associated with only
            # 1 type of quantity vector. Unless you include
            # weird non-SI units like second/minute, which refer
            # to both time and plane angle. But I'm not going
            # to include them.
            assert quantity_vector == QUANTITY_TO_QV[q]
        else:
            QUANTITY_TO_QV[q] = quantity_vector
        QV_TO_QUANTITY[quantity_vector].append(q)
    
    assert singular_name not in NAME_TO_UNIT
    assert plural_name not in NAME_TO_UNIT
    assert symbol not in SYMBOL_TO_UNIT
    NAME_TO_UNIT[singular_name] = unit
    NAME_TO_UNIT[plural_name] = unit
    SYMBOL_TO_UNIT[symbol] = unit

    # return this so that it can be reused when
    # defining other units.
    return quantity_vector

class Quantities:
    TIME = "time"
    LENGTH = "length"
    MASS = "mass"
    ELECTRIC_CURRENT = "electric current"
    THERMODYNAMIC_TEMP = "thermodynamic temperature"
    AMOUNT_OF_SUBSTANCE = "amount of substance"
    LUMINOUS_INTENSITY = "luminous intensity"

QSPACE = QuantitySpace(["kg", "m", "s", "A", "K", "mol", "cd"])
KG = QSPACE.get_basis_vector("kg")
M = QSPACE.get_basis_vector("m")
S = QSPACE.get_basis_vector("s")
A = QSPACE.get_basis_vector("A")
K = QSPACE.get_basis_vector("K")
MOL = QSPACE.get_basis_vector("mol")
CD = QSPACE.get_basis_vector("cd")

## Base units.
register_unit("s", "second", Quantities.TIME, S)
register_unit("m", "metre", Quantities.LENGTH, M)
# Nice edge case, Obama.
register_unit("g", "gram", Quantities.MASS, KG, multiple=rat(1,1000))
register_unit("A", "ampere", Quantities.ELECTRIC_CURRENT, A)
register_unit("K", "kelvin", Quantities.THERMODYNAMIC_TEMP, K)
register_unit("mol", "mole", Quantities.AMOUNT_OF_SUBSTANCE, MOL)
# The worst unit, apparently.
register_unit("cd", "candela", Quantities.LUMINOUS_INTENSITY, CD)

# TODO: write a scraper for these Wikipedia pages to get all the units.
# As much as possible. Otherwise, I'll have a lot of tedious typing to
# do. There may be other "fun" units I can incorporate.
#   https://en.wikipedia.org/wiki/International_System_of_Units
#   https://en.wikipedia.org/wiki/SI_derived_unit
#   https://en.wikipedia.org/wiki/Non-SI_units_mentioned_in_the_SI
