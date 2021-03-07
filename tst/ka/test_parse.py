import pytest

from ka.parse import parse_tokens, ParseNode, ParsingError
from ka.tokens import Token, Tokens

def t(tag, **kwargs):
    # Don't care about the indexes.
    return Token(tag, 0, 0, **kwargs)

def validate_parse(tokens, expected_tree):
    actual_tree = parse_tokens(tokens)
    actual_stack = [actual_tree]
    expected_stack = [expected_tree]
    while actual_stack and expected_stack:
        a_node = actual_stack.pop()
        e_node = expected_stack.pop()
        assert a_node.label == e_node.label
        actual_stack.extend(a_node.children)
        expected_stack.extend(e_node.children)
    assert not actual_stack and not expected_stack

def test_parse_assignment():
    validate_parse(
        [t(Tokens.VAR, name="x"),
         t(Tokens.ASSIGNMENT_OP),
         t(Tokens.NUM, value=5)],
        ParseNode("", children=[ParseNode("x", children=[ParseNode(5)])]))

def test_parse_arithmetic():
    validate_parse(
        [t(Tokens.NUM, value=3),
         t(Tokens.PLUS),
         t(Tokens.NUM, value=5)],
        ParseNode("",
            children=[
                ParseNode("+",
                          children=[ParseNode(3),
                                    ParseNode(5)])]))

def test_parse_associativity():
    # 7*3/2
    validate_parse(
        [t(Tokens.NUM, value=7),
         t(Tokens.MULT),
         t(Tokens.NUM, value=3),
         t(Tokens.DIV),
         t(Tokens.NUM, value=2)],
        ParseNode("",
            children=[
                ParseNode("/",
                    children=[
                        ParseNode("*",
                            children=[ParseNode(7), ParseNode(3)]),
                        ParseNode(2)])]))
                        
def test_parse_multiple_statements():
    validate_parse(
        [t(Tokens.VAR, name="x"),
         t(Tokens.ASSIGNMENT_OP),
         t(Tokens.NUM, value=0),
         t(Tokens.STATEMENT_SEPARATOR),
         t(Tokens.VAR, name="x")],
        ParseNode("",
            children=[
                ParseNode("x", children=[ParseNode(0)]),
                ParseNode("x")]))

def test_parse_no_tokens():
    validate_parse([], ParseNode("", children=[]))

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
        ParseNode("",
            children=[
                ParseNode("*",
                    children=[
                        ParseNode("feet^2 s^1 | Pa^-1",
                            children=[ParseNode("x")]),
                        ParseNode("metres^1",
                            children=[
                                ParseNode("y")])])]))

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
