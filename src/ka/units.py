import collections
from fractions import Fraction as frac
import math

QUANTITY_TO_QV = {} # <-- this is used only to check for mistakes
QV_TO_QUANTITY = collections.defaultdict(list)
NAME_TO_UNIT = {}
SYMBOL_TO_UNIT = {}
UNITS = []

class Prefix:
    def __init__(self, name_prefix, symbol_prefix, exp):
        self.name_prefix = name_prefix
        self.symbol_prefix = symbol_prefix
        self.multiplier = 10**exp if exp>0 else frac(1, 10**-exp)

MILLI_PREFIX = Prefix("milli", "m", -3)

PREFIXES = [
    Prefix("yotta", "Y", 24),
    Prefix("zetta", "Z", 21),
    Prefix("exa", "E", 18),
    Prefix("peta", "P", 15),
    Prefix("tera", "T", 12),
    Prefix("giga", "G", 9),
    Prefix("mega", "M", 6),
    Prefix("kilo", "k", 3),
    Prefix("hecto", "h", 2),
    Prefix("deca", "da", 1),
    Prefix("deci", "d", -1),
    Prefix("centi", "c", -2),
    MILLI_PREFIX,
    Prefix("micro", "μ", -6),
    Prefix("nano", "n", -9),
    Prefix("pico", "p", -12),
    Prefix("femto", "f", -15),
    Prefix("atto", "a", -18),
    Prefix("zepto", "z", -21),
    Prefix("yocto", "y", -24)
]

class InvalidPrefixError(Exception):
    pass

def lookup_unit(name):
    """Returns Unit by the given name, if it
    exists. Otherwise, return None.
    Raises InvalidPrefixError if a prefix is applied to
    a unit with an offset, as doing so doesn't make sense."""
    if name in NAME_TO_UNIT:
        return NAME_TO_UNIT[name]
    if name in SYMBOL_TO_UNIT:
        return SYMBOL_TO_UNIT[name]
    for prefix in PREFIXES:
        unprefixed = name[len(prefix.name_prefix):]
        if name.startswith(prefix.name_prefix) and unprefixed in NAME_TO_UNIT:
            return apply_prefix(prefix, NAME_TO_UNIT[unprefixed])
        unprefixed = name[len(prefix.symbol_prefix):]
        if name.startswith(prefix.symbol_prefix) and unprefixed in SYMBOL_TO_UNIT:
            return apply_prefix(prefix, SYMBOL_TO_UNIT[unprefixed])
    return None

def apply_prefix(prefix, unit):
    # Don't need to update any of the other unit data besides
    # the multiple, since the other stuff won't be used anywhere.
    if unit.offset != 0:
        raise InvalidPrefixError()
    return Unit(unit.symbol, unit.singular_name, unit.plural_name, unit.quantities,
                unit.quantity_vector, prefix.multiplier * unit.multiple, unit.offset)

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

    def __str__(self):
        return "QuantityVector(" + self.prettified() + ")"

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

def register_unit(symbol, singular_name, quantities, quantity_vector,
        plural_name=None, multiple=1, offset=0):
    assert isinstance(quantity_vector, QuantityVector)
    if plural_name is None:
        plural_name = singular_name + "s"
    if isinstance(quantities, str):
        quantities = [quantities]

    unit = Unit(symbol, singular_name, plural_name, quantities,
                quantity_vector, multiple, offset)

    global QUANTITY_TO_QV, QV_TO_QUANTITY, NAME_TO_UNIT, SYMBOL_TO_UNIT, UNITS

    UNITS.append(unit)

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
    return unit

def register_derived_unit(symbol, singular_name, base_unit, multiple=1, plural_name=None):
    """Registers a unit based on another unit.
    i.e. it should be a measure of the same quantity."""
    return register_unit(symbol, singular_name, base_unit.quantities,
                         base_unit.quantity_vector, multiple=base_unit.multiple*multiple,
                         plural_name=plural_name)

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
# Useful references:
register_unit("s", "second", "time", S)
register_unit("m", "metre", "length", M)
# Nice edge case, Obama.
GRAM = register_unit("g", "gram", "mass", KG, multiple=frac(1,1000))
register_unit("A", "ampere", "electric current", A)
register_unit("K", "kelvin", "thermodynamic temperature", K)
register_unit("mol", "mole", "amount of substance", MOL)
# The worst unit, apparently.
register_unit("cd", "candela", "luminous intensity", CD)

## Named units, derived from SI base units.
##   https://en.wikipedia.org/wiki/SI_derived_unit
## And other useful lists:
##   https://en.wikipedia.org/wiki/International_System_of_Units
##   https://en.wikipedia.org/wiki/Non-SI_units_mentioned_in_the_SI
##   https://www.adducation.info/how-to-improve-your-knowledge/units-of-measurement/
## If I don't make a mistake here somewhere, it'll be a miracle.
## I should really write a script to parse the wiki.
# Also, it's rather confusing that I pass around both
# QuantityVectors and Units.
register_unit("Hz", "hertz", "frequency", S**-1, plural_name=Unit.NO_PLURAL)
RAD = M/M
register_unit("rad", "radian", "angle", RAD)
register_unit("sr", "steradian", "solid angle", M**2 / M**2)
register_unit("N", "newton", ["force", "weight"], KG * M * S**-2)
PASCAL = KG * M**-1 * S**-2
register_unit("Pa", "pascal", ["pressure", "stress"], PASCAL)
J = KG * M**2 * S**-2
register_unit("J", "joule", ["energy", "work", "heat"], J)
WATT = KG * M**2 * S**-3
register_unit("W", "watt", ["power", "radiant flux"], WATT)
C = S * A
register_unit("C", "coulomb", ["electric charge", "quantity of electricity"], C)
V = J / C
register_unit("V", "volt", ["voltage", "electrical potential difference", "electromotive force"], V)
register_unit("F", "farad", "electrical capacitance", C / V)
register_unit("ohm", "ohm", "electrical resistance", V / A)
register_unit("S", "siemens", "electrical conductance", A / V, plural_name=Unit.NO_PLURAL)
register_unit("Wb", "weber", "magnetix flux", V * S)
register_unit("T", "tesla", ["magnetic induction", "magnetic flux density"], KG * S**-2 * A**-1)
register_unit("H", "henry", "electrical inductance", V * S / A, plural_name="henries")
# To go from degrees Celcius to Kelvin, add 273.15 = 5463/20.
register_unit("degC", "degC", "thermodynamic temperature", K, offset=frac(5463, 20))
register_unit("lm", "lumen", "luminous flux", CD)
register_unit("lx", "lux", "illuminance", CD * M**-2, plural_name=Unit.NO_PLURAL)
register_unit("Bq", "becquerel", "radioactivity", S**-1)
register_unit("Gy", "gray", "absorbed dose", J / KG)
register_unit("Sv", "sievert", "equivalent dose", J / KG)
register_unit("kat", "katal", "catalytic activity", MOL * S**-1)

### Fucked up units.
register_unit("min", "minute", "time", S, multiple=60)
register_unit("h", "hour", "time", S, multiple=3600)
register_unit("d", "day", "time", S, multiple=86400)
register_unit("au", "astronomicalunit", "length", M, multiple=149597870700)
register_unit("deg", "degree", "angle", RAD, multiple=math.pi/180)
register_unit("ha", "hectare", "area", M**2, multiple=10**4)
register_unit("acre", "acre", "area", M**2, multiple=4046.8564224)
LITRE = register_unit("l", "litre", "volume", M**3, multiple=frac(1, 10**3))
MILLILITRE = apply_prefix(MILLI_PREFIX, LITRE)
register_unit("t", "tonne", "mass", KG, multiple=1000)
register_unit("Da", "dalton", "mass", KG, multiple=1.660539040e-27)
register_unit("eV", "electronvolt", "energy", J, multiple=1.602176634e-19)
register_unit("lj", "lightyear", "length", M, multiple=9.4607e15)
register_unit("pc", "parsec", "length", M, multiple=3.0857e16)
INCH = register_unit("in", "inch", "length", M, multiple=0.0254, plural_name="inches")
FEET = register_derived_unit("ft", "foot", INCH, multiple=12, plural_name="feet")
YARD = register_derived_unit("yd", "yard", FEET, multiple=3)
register_derived_unit("mi", "mile", YARD, multiple=1760)
register_unit("sm", "nauticalmile", "length", M, multiple=1852)
# Using UK / Imperial measures for teaspoon and whatnot. As
# opposed to US measures.
# https://en.wikipedia.org/wiki/Cooking_weights_and_measures
register_derived_unit("tsp", "teaspoon", MILLILITRE, multiple=5.91939)
register_derived_unit("tbsp", "tablespoon", MILLILITRE, multiple=17.7582)
register_derived_unit("floz", "fluidounce", MILLILITRE, multiple=28.4130625)
register_derived_unit("cup", "cup", MILLILITRE, multiple=284.13)
register_derived_unit("gill", "gill", MILLILITRE, multiple=142.0653125)
register_derived_unit("pt", "pint", MILLILITRE, multiple=586.26125)
register_derived_unit("qt", "quart", MILLILITRE, multiple=1136.5225)
register_derived_unit("gal", "gallon", MILLILITRE, multiple=4546.09)
register_derived_unit("gr", "grain", GRAM, multiple=0.0648)
register_derived_unit("dr", "dram", GRAM, multiple=1.77)
register_derived_unit("oz", "ounce", GRAM, multiple=28.35)
register_unit("lb", "pound", "mass", KG, multiple=0.45)
register_unit("hp", "horsepower", "power", WATT, multiple=735.5)
register_unit("bar", "bar", "pressure", PASCAL, multiple=100000)
register_unit("cal", "calorie", "energy", J, multiple=4.1868)
