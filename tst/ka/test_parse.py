import pytest

from ka.parse import parse_tokens, ParseNode, ParsingError, UnitSignature
from ka.tokens import Token, Tokens

def t(tag, **kwargs):
    # Don't care about the indexes.
    return Token(tag, 0, 0, **kwargs)

def pn(value, children=None):
    if children is None:
        children = []
    if isinstance(children, ParseNode):
        children = [children]
    return ParseNode(value=value, children=children)

def validate_parse(tokens, expected_tree_children):
    # All the expected inputs implicitly have a root node.
    if isinstance(expected_tree_children, ParseNode):
        expected_tree_children = [expected_tree_children]
    expected_tree = pn(None, expected_tree_children)
    actual_tree = parse_tokens(tokens)
    actual_stack = [actual_tree]
    expected_stack = [expected_tree]
    while actual_stack and expected_stack:
        a_node = actual_stack.pop()
        e_node = expected_stack.pop()
        # Here, we only compare the values of the nodes, which
        # shows that the tree has the right structure. Some of the
        # other attributes of the tree, such as evaluation mode, are
        # tested implicitly in the test suite for evaluation.
        assert a_node.value == e_node.value
        actual_stack.extend(a_node.children)
        expected_stack.extend(e_node.children)
    assert not actual_stack and not expected_stack

def test_parse_assignment():
    validate_parse(
        [t(Tokens.VAR, name="x"),
         t(Tokens.ASSIGNMENT_OP),
         t(Tokens.NUM, value=5)],
        pn("x", [pn(5)]))

def test_parse_arithmetic():
    validate_parse(
        [t(Tokens.NUM, value=3),
         t(Tokens.PLUS),
         t(Tokens.NUM, value=5)],
        pn("+", [pn(3), pn(5)]))

def test_parse_associativity():
    # 7*3/2
    validate_parse(
        [t(Tokens.NUM, value=7),
         t(Tokens.MULT),
         t(Tokens.NUM, value=3),
         t(Tokens.DIV),
         t(Tokens.NUM, value=2)],
        pn("/", [pn("*", [pn(7), pn(3)]), pn(2)]))

def test_parse_multiple_statements():
    validate_parse(
        [t(Tokens.VAR, name="x"),
         t(Tokens.ASSIGNMENT_OP),
         t(Tokens.NUM, value=0),
         t(Tokens.STATEMENT_SEPARATOR),
         t(Tokens.VAR, name="x")],
        [pn("x", [pn(0)]), pn("x")])

def test_parse_no_tokens():
    validate_parse([], [])

def validate_parsing_error(tokens):
    with pytest.raises(ParsingError):
        parse_tokens(tokens)

def test_parse_unclosed_parentheses():
    validate_parsing_error([t(Tokens.LBRACKET), t(Tokens.NUM, value=1)])

def test_parse_empty_parentheses():
    validate_parsing_error([t(Tokens.LBRACKET), t(Tokens.RBRACKET)])

def test_parse_adjacent_values_without_operator():
    validate_parsing_error([t(Tokens.NUM, value=1), t(Tokens.NUM, value=2)])

def test_parse_binary_op_with_missing_right_operand():
    validate_parsing_error([t(Tokens.NUM, value=1), t(Tokens.PLUS)])

def test_parse_binary_op_with_missing_left_operand():
    validate_parsing_error([t(Tokens.NUM, value=2), t(Tokens.NUM, value=1)])

def test_parse_units():
    validate_parse(
        [t(Tokens.VAR, name="x"),
         t(Tokens.VAR, name="feet"),
         t(Tokens.EXP),
         t(Tokens.NUM, value=2),
         t(Tokens.VAR, name="s"),
         t(Tokens.UNIT_DIVIDE),
         t(Tokens.VAR, name="Pa"),
         t(Tokens.EXP),
         t(Tokens.NUM, value=-1),
         t(Tokens.MULT),
         t(Tokens.VAR, name="y"),
         t(Tokens.VAR, name="metres")],
        pn("*",
           [pn(UnitSignature([("feet", 2), ("s", 1)], [("Pa", -1)]),
               pn("x")),
            pn(UnitSignature([("metres", 1)], []),
               pn("y"))]))

def test_parse_units_when_non_integer_exponent():
    validate_parsing_error([
        t(Tokens.VAR, name="x"),
        t(Tokens.VAR, name="m"),
        t(Tokens.EXP),
        t(Tokens.NUM, value=1.2)])

def test_parse_units_when_missing_units_after_divide():
    validate_parsing_error([
        t(Tokens.VAR, name="x"),
        t(Tokens.VAR, name="m"),
        t(Tokens.EXP),
        t(Tokens.NUM, value=2),
        t(Tokens.UNIT_DIVIDE)])

def test_parse_comparison():
    validate_parse(
        [t(Tokens.NUM, value=1), t(Tokens.LT), t(Tokens.VAR, name="X")],
        pn("<", [pn(1), pn("X")]))

def test_parse_double_comparison():
    validate_parse(
        [t(Tokens.NUM, value=1),
         t(Tokens.LT),
         t(Tokens.VAR, name="X"),
         t(Tokens.LEQ),
         t(Tokens.NUM, value=3)],
        pn("< <=", [pn(1), pn("X"), pn(3)]))

def test_fails_more_than_two_compares():
    validate_parsing_error(
        [t(Tokens.NUM, value=1),
         t(Tokens.LT),
         t(Tokens.VAR, name="X"),
         t(Tokens.LEQ),
         t(Tokens.NUM, value=3),
         t(Tokens.LEQ),
         t(Tokens.NUM, value=5)])

def test_parse_interval():
    validate_parse(
        [t(Tokens.INTERVAL_OPEN),
         t(Tokens.NUM, value=1),
         t(Tokens.INTERVAL_SEPARATOR),
         t(Tokens.NUM, value=10),
         t(Tokens.INTERVAL_CLOSE)],
        pn("range", [pn(1), pn(10)]))

def test_parse_array():
    validate_parse(
        [t(Tokens.ARRAY_OPEN),
         t(Tokens.NUM, value=1),
         t(Tokens.ARRAY_SEPARATOR),
         t(Tokens.NUM, value=2),
         t(Tokens.ARRAY_SEPARATOR),
         t(Tokens.NUM, value=3),
         t(Tokens.ARRAY_CLOSE)],
        pn("{...}", [pn(1), pn(2), pn(3)]))

def test_parse_array_with_conditions():
    validate_parse(
        [t(Tokens.ARRAY_OPEN),
         t(Tokens.VAR, name="x"),
         t(Tokens.ARRAY_CONDITION_SEP),
         t(Tokens.VAR, name="x"),
         t(Tokens.ELEMENT_OF),
         t(Tokens.INTERVAL_OPEN),
         t(Tokens.NUM, value=1),
         t(Tokens.INTERVAL_SEPARATOR),
         t(Tokens.NUM, value=3),
         t(Tokens.INTERVAL_CLOSE),
         t(Tokens.ARRAY_SEPARATOR),
         t(Tokens.VAR, name="x"),
         t(Tokens.LEQ),
         t(Tokens.NUM, value=2),
         t(Tokens.ARRAY_CLOSE)],
        pn("{...}",
            [pn("x"),
             pn("range", [pn(1), pn(3)]),
             pn("<=", [pn("x"), pn(2)])]))

