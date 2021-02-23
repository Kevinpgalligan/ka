from .functions import multiply
from .types import number

class Quantities:
    TIME = "time"
    LENGTH = "length"
    MASS = "mass"
    ELECTRIC_CURRENT = "electric current"
    THERMODYNAMIC_TEMP = "thermodynamic temperature"
    AMOUNT_OF_SUBSTANCE = "amount of substance"
    LUMINOUS_INTENSITY = "luminous intensity"

# Need to define:
# 1. multiplication & so on, defined in terms of other units & in terms
#    of numbers.
# 2. a way of simplifying the unit and extracting the multiplier?
#    so, when creating a quantity, you wanna simplify the unit by
#    taking the multiplier and applying it to the magnitude/value
#    of the quantity.
# I'm thinking through cases here.
# 5 feet^2: first, we fetch the feet unit, which already has a multiplier
#           applied to metres. Then we square it, which affects the multipler
#           and the dimension signature / whatever. Then we form a quantity
#           by applying the multiplier and getting it in terms of base units.
#           The unit of a quantity may not have a name!
#           For example, what about 5 feet^2 s^-1? It doesn't have a symbol.
#           I think a quantity might end up having a unit signature rather than
#           a unit. We can fetch a unit / name for it when displaying.
# THIS IS SO DIFFICULT TO MODEL.
#class Unit:
#    def __init__(self, symbol, names, quantity, multiplier=number(1)):
#        self.symbol = symbol
#        self.names = names
#        self.quantity = quantity
#        self.multiplier = multiplier
#
#UNIT_MAP = {}
#
#def register_unit(symbol, singular_name, quantity):
#    global UNIT_MAP
#    unit = Unit(symbol, [singular_name, singular_name+"s"], quantity)
#
#
#S = register_unit("s", "second", "time")

class Vector:
    def __init__(self, xs):
        self.xs = xs

    def __len__(self):
        return len(self.xs)

    def __eq__(self, other):
        return isinstance(other, Vector) and all(x==y for x, y in zip(self.xs, other.xs))

    def __add__(self, other):
        return Vector([x+y for x, y in zip(self.xs, other.xs)])

    def __rmul__(self, a):
        return self.__mul__(a)

    def __mul__(self, a):
        return Vector([a*x for x in self.xs])

    def __str__(self):
        return "<" + ",".join(str(x) for x in self.xs) + ">"

    def __repr__(self):
        return str(self)

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
            Vector([1 if name==basis_name else 0 for name in self.base_units]),
            self.base_units)

QSPACE = QuantitySpace(["kg", "m", "s", "A", "K", "mol", "cd"])
KG = QSPACE.get_basis_vector("kg")
M = QSPACE.get_basis_vector("m")
S = QSPACE.get_basis_vector("s")
A = QSPACE.get_basis_vector("A")
K = QSPACE.get_basis_vector("K")
MOL = QSPACE.get_basis_vector("mol")
CD = QSPACE.get_basis_vector("cd")

# API:
#   register_unit("N", "newton", Measures.FORCE, KG * M * S**-2)
# Also, g can be a unit, it just needs a multiple of 1/1000. kg doesn't
# need to be defined as its own unit. And then the kilo prefix will UNDO
# that multiple. PERFECT. THE PROBLEM IS SOLVED!
