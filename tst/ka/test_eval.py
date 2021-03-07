import math

import pytest

from ka.tokens import tokenise
from ka.parse import parse_tokens
from ka.eval import eval_parse_tree, EvalError
from ka.types import Quantity, Number, number, rational
from ka.functions import multiply
from ka.units import M, S, K

def validate_result(s, expected):
    tokens = tokenise(s)
    tree = parse_tokens(tokens)
    assert expected == eval_parse_tree(tree)

def validate_results(cases):
    for s, expected in cases:
        validate_result(s, expected)

def validate_fail(s):
    with pytest.raises(EvalError):
        eval_parse_tree(parse_tokens(tokenise(s)))

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
    validate_result("3/4", rational(3, 4))

def test_simplification():
    validate_result("1.0", 1)
    validate_result("4/2", 2)

def test_coercion():
    # Hmmm, might result in shitty floating
    # point shit.
    validate_result("(3/2)*1.2",
                    multiply(rational(3, 2), number(1.2)))

def test_equations_and_functions():
    validate_results([
        ("r=2.5;pi*r^2", math.pi * 2.5**2),
        ("x=3;x^2+2*x+1", 16),
        ("n=5;n*(n+1)/2", 15),
        ("(3/2)%1", rational(1, 2)),
        ("(3/2)^2", rational(9, 4)),
        ("-1+2", 1),
        ("+1+2", 3),
        ("sin(0)", 0),
        ("cos(0)", 1),
        ("tan(0)", 0),
        ("sqrt(4)", 2),
        ("ln(e)", 1),
        ("log10(10)", 1),
        ("log2(2)", 1),
        ("abs(-3/2)", rational(3, 2)),
        ("floor(1.7)", 1),
        ("ceil(1.7)", 2),
        ("round(1.4)", 1),
        ("i(1.8+0.5)", 2),
        ("f(3/2)", 1.5),
        ("log(2, 2)", 1),
        ("C(3,1)", 3),
        ("3!", 6),
    ])

def test_quantities():
    validate_results([
        ("5 m | s", Quantity(5, M / S)),
        ("3m^2 s^-1", Quantity(3, M**2 * S**-1)),
        ("100 degC", Quantity(-rational(3463, 20), K)),
        ("5 feet seconds", Quantity(0.3048*5, M * S))])

def test_quantity_of_quantity():
    validate_fail("(5m)s")

def test_unknown_unit():
    validate_fail("10 flabberglooks | second")

def test_offset_unit_with_exponent():
    validate_fail("10 degC^2")

def test_offset_unit_with_other_units():
    validate_fail("10 degC seconds")

def test_unit_prefixes():
    validate_results([
        ("5 km", Quantity(5000, M)),
        ("1 kilometre", Quantity(1000, M)),
        ("3 m | millisecond", Quantity(3000, M / S))])

def test_prefix_for_offset_unit():
    validate_fail("1 kilodegC")
