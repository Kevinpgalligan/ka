import math

from ka.tokens import tokenise
from ka.parse import parse_tokens
from ka.eval import eval_parse_tree
from ka.types import Number, number, rational
from ka.functions import multiply

def validate_result(s, expected):
    tokens = tokenise(s)
    tree = parse_tokens(tokens)
    assert expected == eval_parse_tree(tree)

def validate_results(cases):
    for s, expected in cases:
        validate_result(s, expected)

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
