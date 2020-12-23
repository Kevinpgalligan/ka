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
