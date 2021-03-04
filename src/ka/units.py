from .functions import multiply

import collections
from fractions import Fraction as frac

QUANTITY_TO_QV = {} # <-- this is used only to check for mistakes
QV_TO_QUANTITY = collections.defaultdict(list)
NAME_TO_UNIT = {}
SYMBOL_TO_UNIT = {}

def lookup_unit(name):
    """Returns Unit by the given name, if it
    exists. Otherwise, return None."""
    if name in NAME_TO_UNIT:
        return NAME_TO_UNIT[name]
    if name in SYMBOL_TO_UNIT:
        return SYMBOL_TO_UNIT[name]
    # TODO unit prefixes
    return None

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

    def __truediv__(self, other):
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

    def get_zero(self):
        return QuantityVector(Vector(tuple(0 for _ in self.base_units)), self.base_units)

class Unit:
    NO_PLURAL = "noplural"

    def __init__(self, symbol, singular_name, plural_name, quantities,
                 quantity_vector, multiple, offset):
        self.symbol = symbol
        self.singular_name = singular_name
        self.plural_name = plural_name
        self.quantities = quantities
        self.quantity_vector = quantity_vector
        self.multiple = multiple
        self.offset = offset

class UnitSignature:
    def __init__(self, quantity_vector, multiple, offset):
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
    assert symbol not in SYMBOL_TO_UNIT
    NAME_TO_UNIT[singular_name] = unit
    SYMBOL_TO_UNIT[symbol] = unit

    if plural_name != Unit.NO_PLURAL:
        assert plural_name not in NAME_TO_UNIT
        NAME_TO_UNIT[plural_name] = unit

    # return this so that it can be reused when
    # defining other units.
    return quantity_vector

## Here's the "space" based on the base units we wanna use.
## All quantities exist within this space.
QSPACE = QuantitySpace(["kg", "m", "s", "A", "K", "mol", "cd"])
KG = QSPACE.get_basis_vector("kg")
M = QSPACE.get_basis_vector("m")
S = QSPACE.get_basis_vector("s")
A = QSPACE.get_basis_vector("A")
K = QSPACE.get_basis_vector("K")
MOL = QSPACE.get_basis_vector("mol")
CD = QSPACE.get_basis_vector("cd")

## SI base units.
register_unit("s", "second", "time", S)
register_unit("m", "metre", "length", M)
# Nice edge case, Obama.
register_unit("g", "gram", "mass", KG, multiple=frac(1,1000))
register_unit("A", "ampere", "electric current", A)
register_unit("K", "kelvin", "thermodynamic temperature", K)
register_unit("mol", "mole", "amount of substance", MOL)
# The worst unit, apparently.
register_unit("cd", "candela", "luminous intensity", CD)

## Named units, derived from SI base units.
## https://en.wikipedia.org/wiki/SI_derived_unit
## If I don't make a mistake here somewhere, it'll be a miracle.
## I should really write a script to parse the wiki.
register_unit("Hz", "hertz", "frequency", S**-1, plural_name=Unit.NO_PLURAL)
register_unit("rad", "radian", "angle", M / M)
register_unit("sr", "steradian", "solid angle", M**2 / M**2)
register_unit("N", "newton", ["force", "weight"], KG * M * S**-2)
register_unit("Pa", "pascal", ["pressure", "stress"], KG * M**-1 * S**-2)
J = register_unit("J", "joule", ["energy", "work", "heat"], KG * M**2 * S**-2)
register_unit("W", "watt", ["power", "radiant flux"], KG * M**2 * S**-3)
C = register_unit("C", "coulomb", ["electric charge", "quantity of electricity"], S * A)
V = register_unit("V", "volt", ["voltage", "electrical potential difference", "electromotive force"], J / C)
register_unit("F", "farad", "electrical capacitance", C / V)
register_unit("Ω", "ohm", "electrical resistance", V / A)
register_unit("S", "siemens", "electrical conductance", A / V, plural_name=Unit.NO_PLURAL)
register_unit("Wb", "weber", "magnetix flux", V * S)
register_unit("T", "tesla", ["magnetic induction", "magnetic flux density"], KG * S**-2 * A**-1)
register_unit("H", "henry", "electrical inductance", V * S / A, plural_name="henries")
# Degrees celcius is offset from 0 kelvin by -273.15 = -5463/20.
register_unit("°C", "degC", "thermodynamic temperature", K, offset=-frac(5463, 20))
register_unit("lm", "lumen", "luminous flux", CD)
register_unit("lx", "lux", "illuminance", CD * M**-2, plural_name=Unit.NO_PLURAL)
register_unit("Bq", "becquerel", "radioactivity", S**-1)
register_unit("Gy", "gray", "absorbed dose", J / KG)
register_unit("Sv", "sievert", "equivalent dose", J / KG)
register_unit("kat", "katal", "catalytic activity", MOL * S**-1)

# TODO
# Add all these units:
#   https://en.wikipedia.org/wiki/International_System_of_Units
#   https://en.wikipedia.org/wiki/Non-SI_units_mentioned_in_the_SI
# Then run some tests to validate the units.
# Check if that all words used in quantities are in the dictionary.
# Check that all symbol / unit names are on the wiki page.
# Check that no quantities have a distance of <=2 (or sth) from each other.
# And so on.
