import math
import abc
import fractions

def number(x):
    n = get_initial_type(x)
    while n.can_move_down():
        n = n.move_down()
    return n

def get_initial_type(x):
    if isinstance(x, float):
        return Float(x)
    if isinstance(x, int):
        return Integer(x)
    if isinstance(x, fractions.Fraction):
        return Rational(x)
    raise TypeError(f"Tried to cast '{type(x)}' to a number.")

def coerce(n1, n2):
    if type(n1) == type(n2):
        return n1, n2
    # Take the lower type & move it up the hierarchy
    # until it has the same type as the higher one.
    ns = [n1, n2]
    low_i = max((0, 1), key=lambda i: TYPE_HIERARCHY.index(type(ns[i])))
    high_i = (low_i+1)%2
    while type(ns[low_i]) != type(ns[high_i]):
        ns[low_i] = ns[low_i].move_up()
    return ns

class Number(abc.ABC):
    @abc.abstractmethod
    def can_move_down(self):
        pass

    @abc.abstractmethod
    def move_down(self):
        pass

    @abc.abstractmethod
    def move_up(self):
        pass

    def __repr__(self):
        return "Number[" + str(self.x) + "]"

    def __str__(self):
        return str(self.x)

    def __eq__(self, y):
        return self.x == y

class Float(Number):
    def __init__(self, x):
        self.x = x

    def can_move_down(self):
        fraction, whole = math.modf(self.x)
        return fraction == 0

    def move_down(self):
        # Go straight to integers. Converting floats
        # to rationals results in ugly-looking fractions
        # due to rounding issues.
        return Integer(int(math.modf(self.x)[1]))

    def move_up(self):
        raise TypeError(
            "Tried to move a float up the type hierarchy.")

def divide(x, y):
    # Assuming they've been converted to have
    # the same type.
    if isinstance(x, int):
        return fractions.Fraction(x, y)
    return x/y

class Rational(Number):
    def __init__(self, x):
        self.x = x

    def can_move_down(self):
        return self.x.denominator == 1

    def move_down(self):
        return Integer(self.x.numerator // self.x.denominator)

    def move_up(self):
        return Float(float(self.x))

    def numerator(self):
        return self.x.numerator

    def denominator(self):
        return self.x.denominator

    def __str__(self):
        return f"{self.x.numerator}/{self.x.denominator}"

class Integer(Number):
    def __init__(self, x):
        self.x = x

    def can_move_down(self):
        return False

    def move_down(self):
        raise TypeError(
            "Tried to convert an integer to a 'simpler' type, but there is none!")

    def move_up(self):
        return Rational(fractions.Fraction(self.x, 1))

    def numerator(self):
        return self.x

    def denominator(self):
        return 1

TYPE_HIERARCHY = [
    Float,
    Rational,
    Integer
]
