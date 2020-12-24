from fractions import Fraction
import math

from ka.tokens import tokenise
from ka.parse import parse_tokens
from ka.eval import eval_parse_tree

def validate_result(s, expected):
    tokens = tokenise(s)
    tree = parse_tokens(tokens)
    assert expected == eval_parse_tree(tree)

def test_empty():
    validate_result("", None)

def test_arithmetic():
    validate_result("1+2*3-3^2", -2)

def test_associativity():
    validate_result("2*3%2", 0)

def test_variables():
    validate_result("x=3;5*x", 15)

def test_overriding_constants():
    validate_result("pi=3.14;pi", 3.14)

def test_rational():
    validate_result("3/4", Fraction(3, 4))

def test_simplification():
    validate_result("1.0", 1)
    validate_result("4/2", 2)

def test_coercion():
    # Hmmm, might result in shitty floating
    # point shit.
    validate_result("(3/2)*1.2", Fraction(3, 2)*1.2)

def test_some_equations():
    validate_result("r=2.5;pi*r^2", math.pi * 2.5**2)
    validate_result("x=3;x^2+2*x+1", 16)
    validate_result("n=5;n*(n+1)/2", 15)
    validate_result("(3/2)%1", Fraction(1, 2))
    validate_result("(3/2)^2", Fraction(9, 4))
