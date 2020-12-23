import pytest

from ka.tokens import tokenise, Tokens, UnknownTokenError

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
        (Tokens.VAR, "x")
    ]
    s = "=;()+-*/%^123+abc1-22x"
    tokens = tokenise(s)
    actual = [(token.tag, s[token.begin_index_incl:token.end_index_excl])
              for token in tokens]
    assert expected == actual

def test_tokenise_unknown():
    with pytest.raises(UnknownTokenError):
        tokenise("@")

def test_tokenise_empty():
    assert [] == tokenise("")
