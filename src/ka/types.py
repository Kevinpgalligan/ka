import math
import fractions

def number(x):
    n = get_initial_type(x)
    while n.can_move_down():
        n = n.move_down()
    return n

def rational(num, den):
    return Rational(fractions.Fraction(num, den))

def get_initial_type(x):
    if isinstance(x, float):
        return Float(x)
    if isinstance(x, int):
        return Integer(x)
    if isinstance(x, fractions.Fraction):
        return Rational(x)
    raise TypeError(f"Tried to cast '{type(x)}' to a number.")

def coerce(n1, n2):
    if isinstance(n1, type(n2)):
        return move_up(n1, type(n2)), n2
    if isinstance(n2, type(n1)):
        return n1, move_up(n2, type(n1))
    raise TypeError(f"Incompatible types: '{type(n1)}' and '{type(n2)}'.")

def move_up(n, t):
    while type(n) != t:
        n = n.move_up()
    return n

class Number:
    def value(self):
        return self.x

    def can_move_down(self):
        return False

    def move_down(self):
        raise TypeError("Invalid coercion")

    def move_up(self):
        raise TypeError("Invalid coercion")

    def __repr__(self):
        return "Number[" + str(self.x) + "]"

    def __str__(self):
        return str(self.x)

    def __eq__(self, y):
        if isinstance(y, Number):
            return self.value() == y.value()
        if type(y) in [float, int]:
            return self.value() == y
        return False

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

def divide(x, y):
    # Assuming they've been converted to have
    # the same type.
    if isinstance(x, int):
        return fractions.Fraction(x, y)
    return x/y

class Rational(Float):
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

class Integer(Rational):
    def __init__(self, x):
        self.x = x

    def can_move_down(self):
        return False

    def move_down(self):
        raise TypeError("Invalid coercion")

    def move_up(self):
        return Rational(fractions.Fraction(self.x, 1))

    def numerator(self):
        return self.x

    def denominator(self):
        return 1

class Unit:
    def __init__(self):
        pass

class Quantity:
    def __init__(self, n, unit):
        self.n = n
        self.unit = unit
