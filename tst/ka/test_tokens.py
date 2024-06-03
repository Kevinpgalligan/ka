import pytest

from ka.tokens import tokenise, Tokens, UnknownTokenError, BadNumberError

def test_tokenise_valid_tokens():
    expected = [
        (Tokens.ASSIGNMENT_OP, "="),
        (Tokens.STATEMENT_SEPARATOR, ";"),
        (Tokens.LBRACKET, "("),
        (Tokens.RBRACKET, ")"),
        (Tokens.PLUS, "+"),
        (Tokens.MINUS, "-"),
        (Tokens.MULT, "*"),
        (Tokens.DIV, "/"),
        (Tokens.MOD, "%"),
        (Tokens.EXP, "^"),
        (Tokens.NUM, "123"),
        (Tokens.PLUS, "+"),
        (Tokens.VAR, "abc1"),
        (Tokens.MINUS, "-"),
        (Tokens.NUM, "22"),
        (Tokens.VAR, "x"),
        (Tokens.FACTORIAL, "!"),
        (Tokens.UNIT_DIVIDE, "|"),
        (Tokens.NUM, "1e-4"),
        (Tokens.UNIT_CONVERT, "to"),
        (Tokens.LEQ, "<="),
        (Tokens.LT, "<"),
        (Tokens.GT, ">"),
        (Tokens.GEQ, ">="),
        (Tokens.EQ, "=="),
        (Tokens.ELEMENT_OF, "in"),
        (Tokens.INTERVAL_OPEN, "["),
        (Tokens.INTERVAL_CLOSE, "]"),
        (Tokens.ARRAY_OPEN, "{"),
        (Tokens.ARRAY_CLOSE, "}"),
        (Tokens.ARRAY_CONDITION_SEP, ":"),
        (Tokens.ARRAY_SEPARATOR, ","),
    ]
    s = "=;()+-*/%^123+abc1-22x!| 1e-4 to <=<>>= == in[]{}:,"
    tokens = tokenise(s)
    actual = [(token.tag, s[token.begin_index_incl:token.end_index_excl])
              for token in tokens]
    assert expected == actual

def test_tokenise_scientific_notation():
    for s, expected in [("100e-2", 1), ("1.2e-4", 1.2e-4)]:
        token = tokenise(s)[0]
        assert token.meta("value") == expected

def test_tokenise_unknown():
    with pytest.raises(UnknownTokenError):
        tokenise("@")

def test_tokenise_empty():
    assert [] == tokenise("")

def test_alt_bases():
    for expected, t in zip([10, 2, 8, 16, 15, 15],
                            tokenise("0d10 0b10 0o10 0x10 0xf 0xF")):
        assert expected == t.meta("value")

def test_bad_digit_for_base():
    for s in ["0b2", "0o8", "0da"]:
        with pytest.raises(BadNumberError):
            tokenise(s)
