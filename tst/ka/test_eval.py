import math
from fractions import Fraction as frac

import pytest

from ka.tokens import tokenise
from ka.functions import UnknownFunctionError, NoMatchingFunctionSignatureError
from ka.parse import parse_tokens, ParsingError
from ka.eval import eval_parse_tree, EvalError
from ka.types import Quantity, Array
from ka.units import M, S, K

def validate_result(s, expected):
    assert expected == get_result(s)

def get_result(s):
    tokens = tokenise(s)
    tree = parse_tokens(tokens)
    return eval_parse_tree(tree)

def validate_results(cases):
    for s, expected in cases:
        validate_result(s, expected)

def validate_fail(s, error_type=EvalError):
    with pytest.raises(error_type):
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
    validate_result("3/4", frac(3, 4))

def test_simplification():
    validate_result("1.0", 1)
    validate_result("4/2", 2)

def test_fraction_by_float():
    # Hmmm, might result in shitty floating
    # point shit.
    validate_result("(3/2)*1.2", frac(3, 2) * 1.2)

def test_integer_division_gives_fraction():
    r = get_result("1/2")
    assert isinstance(r, frac)

def test_equations_and_functions():
    validate_results([
        ("r=2.5;pi*r^2", math.pi * 2.5**2),
        ("x=3;x^2+2*x+1", 16),
        ("n=5;n*(n+1)/2", 15),
        ("(3/2)%1", frac(1, 2)),
        ("(3/2)^2", frac(9, 4)),
        ("-1+2", 1),
        ("+1+2", 3),
        ("sin(0)", 0),
        ("cos(0)", 1),
        ("tan(0)", 0),
        ("sqrt(4)", 2),
        ("ln(e)", 1),
        ("log10(10)", 1),
        ("log2(2)", 1),
        ("abs(-3/2)", frac(3, 2)),
        ("floor(1.7)", 1),
        ("ceil(1.7)", 2),
        ("round(1.4)", 1),
        ("int(1.8+0.5)", 2),
        ("float(3/2)", 1.5),
        ("log(2, 2)", 1),
        ("C(3,1)", 3),
        ("3!", 6),
    ])

def test_quantities():
    validate_results([
        ("5 m | s", Quantity(5, M / S)),
        ("3m^2 s^-1", Quantity(3, M**2 * S**-1)),
        ("100 degC", Quantity(frac(7463, 20), K)),
        ("5 feet seconds", Quantity(0.0254*12*5, M * S)),
        ("5m to mm", 5000)])

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

def test_unassigned_variable():
    validate_fail("x")

def test_convert_non_quantity():
    validate_fail("5 to m")

def test_convert_incompatible_units():
    validate_fail("5m to s")

def test_prefix_for_offset_unit():
    validate_fail("1 kilodegC")

def test_unknown_function():
    validate_fail("f(1)", UnknownFunctionError)

def test_no_matching_function_signature():
    validate_fail("cos(1, 2)", NoMatchingFunctionSignatureError)

def test_division_by_zero():
    validate_fail("1/0")

def test_overflow():
    validate_fail("1.2^100000000000000000000000")

def test_probability():
    for s, r in [
            # Equality/inequality for continuous/discrete.
            ("P(Uniform(0, 10) < 5)", .5),
            ("P(Uniform(0, 10) <= 5)", .5),
            ("P(UniformInt(1, 10) <= 5)", .5),
            ("P(UniformInt(1, 10) < 5)", .4),
            ("P(UniformInt(1, 10) = 5)", .1),
            # Same thing but reversed.
            ("P(5 > Uniform(0, 10))", .5),
            ("P(5 >= UniformInt(1, 10))", .5),
            ("P(5 > UniformInt(1, 10))", .4),
            # Expectation.
            ("E(Gaussian(2, 1))", 2),
            # Double comparisons.
            ("P(1 <= Uniform(0, 10) <= 3)", .2),
            ("P(1 < UniformInt(1, 10) < 2)", 0),
            ("P(1 < UniformInt(1, 10) <= 2)", .1),
            ("P(1 <= UniformInt(1, 10) < 2)", .1),
            ("P(3 >= Uniform(0, 10) >= 1)", .2),
            ("P(2 > UniformInt(1, 10) > 1)", 0),
            ("P(2 >= UniformInt(1, 10) > 1)", .1),
            ("P(2 > UniformInt(1, 10) >= 1)", .1),
            ]:
        actual_result = get_result(s) 
        assert math.isclose(r, actual_result)

def test_probability_fails():
    for s, err in [("P(5 = UniformInt(1, 10))", NoMatchingFunctionSignatureError),
              ("P(1 < 2)", NoMatchingFunctionSignatureError),
              ("P(1 < Binomial(5, .2) < Poisson(5) < 10)", ParsingError),
              ("P(1 < Binomial(5, .2) = 4)", UnknownFunctionError),
              ("P(1 < Binomial(5, .2) > 4)", UnknownFunctionError),
              ]:
        validate_fail(s, **(dict() if err is None else dict(error_type=err)))

def test_interval():
    validate_results([
        ("[1,5]", Array([1,2,3,4,5])),
        ("N=5; [-5,5]", Array(list(range(-5,6))))
    ])

def test_array():
    validate_results([
        ("{}", Array([])),
        ("{1}", Array([1])),
        ("{1+1,1 m, {}}",
         Array([2,
                Quantity(1, M),
                Array([])]))
    ])

def test_array_with_conditions():
    validate_results([
        ("{x:x in [1,3]}", Array([1,2,3])),
        ("{x:x in [1,3], x <= 2}", Array([1,2])),
    ])

def test_comparison():
    validate_results([
        ("1 == 1", 1),
        ("1 == 2", 0),
        ("2 == 1.5", 0),
        ("1 m == 1 m", 1),
        ("2 m == 1 m", 0),
        ("1 < 2", 1),
        ("1 <= 2", 1),
        ("1 <= 1", 1),
        ("1 <= 0", 0),
        ("1 > 0", 1),
        ("1 >= 0", 1),
        ("-1 >= 0", 0),
        ("-1 > 0", 0),
        ("0 > 0", 0),
    ])
