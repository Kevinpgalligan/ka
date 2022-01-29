import re
from fractions import Fraction as frac

NUM_REGEX = re.compile(
    r"(([0-9]+\.?[0-9]*)|([0-9]*\.?[0-9]+))(e\-?[0-9]+)?")
VAR_REGEX = re.compile(r"[a-zA-Z][_a-zA-Z0-9]*")

class Token:
    def __init__(self, tag, begin_index_incl, end_index_excl, **kwargs):
        self.tag = tag
        self.begin_index_incl = begin_index_incl
        self.end_index_excl = end_index_excl
        self._meta = dict(**kwargs)

    def meta(self, key):
        if key not in self._meta:
            raise Exception(f"Token of type {self.tag} does not have metadata {key}.")
        return self._meta[key]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "".join(["Token[",
                        self.tag,
                        ",", str(self.begin_index_incl),
                        ",", str(self.end_index_excl),
                        "]"])

class Tokens:
    ASSIGNMENT_OP = '='
    STATEMENT_SEPARATOR = ";"
    LBRACKET = '('
    RBRACKET = ')'
    PLUS = '+'
    MINUS = '-'
    MULT = '*'
    DIV = '/'
    MOD = '%'
    EXP = '^'
    VAR = 'identifier'
    NUM = 'number'
    FUNCTION_ARG_SEPARATOR = ','
    FACTORIAL = '!'
    UNIT_DIVIDE = '|'
    UNIT_CONVERT = '>'

CONST_TOKENS = [
    Tokens.ASSIGNMENT_OP,
    Tokens.STATEMENT_SEPARATOR,
    Tokens.LBRACKET,
    Tokens.RBRACKET,
    Tokens.PLUS,
    Tokens.MINUS,
    Tokens.MULT,
    Tokens.DIV,
    Tokens.MOD,
    Tokens.EXP,
    Tokens.FUNCTION_ARG_SEPARATOR,
    Tokens.FACTORIAL,
    Tokens.UNIT_DIVIDE,
    Tokens.UNIT_CONVERT
]

class UnknownTokenError(Exception):
    def __init__(self, index):
        self.index = index

def tokenise(s):
    """
    raises: UnknownTokenError
    """
    i = 0
    i = skip_whitespace(i, s)
    tokens = []
    while i < len(s):
        token = read_token(i, s)
        if token is None:
            raise UnknownTokenError(i)
        i = skip_whitespace(token.end_index_excl, s)
        tokens.append(token)
    return tokens

def skip_whitespace(i, s):
    while i < len(s) and s[i].isspace():
        i += 1
    return i

def read_token(i, s):
    if s[i].isalpha():
        m = VAR_REGEX.match(s, i)
        return Token(Tokens.VAR, m.start(), m.end(), name=m.group(0))
    if s[i].isnumeric() or s[i] == '.':
        return read_num_token(i, s)
    for t in CONST_TOKENS:
        if s.startswith(t, i):
            return Token(t, i, i+len(t))
    return None

def read_num_token(i, s):
    m = NUM_REGEX.match(s, i)
    raw_value = m.group(1)
    # Keep it as an integer if possible.
    if '.' in raw_value:
        value = float(raw_value)
    else:
        value = int(raw_value)
    if m.group(4):
        exponent = int(m.group(4)[1:])
        if exponent < 0:
            value *= frac(1, 10**-exponent)
        else:
            value *= 10**exponent
    return Token(Tokens.NUM, m.start(), m.end(), value=value)
