import re
from fractions import Fraction as frac

NUM_REGEX = re.compile(
    r"""(0(x|o|b|d)([0-9a-fA-F]+))               # Integer with base prefix
        | (([0-9]+\.?[0-9]*)|([0-9]*\.?[0-9]+))  # Decimal, float or integer
          (e\-?[0-9]+)?                          # Scientific notation""",
    re.VERBOSE)
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
    UNIT_CONVERT = 'to'
    EQ = '=='
    LT = '<'
    LEQ = '<='
    GT = '>'
    GEQ = '>='
    ARRAY_OPEN = '{'
    ARRAY_CLOSE = '}'
    ARRAY_SEPARATOR = ','
    ARRAY_CONDITION_SEP = ':'
    ELEMENT_OF = "in"
    INTERVAL_OPEN = "["
    INTERVAL_CLOSE = "]"
    INTERVAL_SEPARATOR = ","
    KW_SEPARATOR = ":"
    STRING = "string"
    INSTANT = "instant"

CONST_TOKENS = [
    # Need to make sure that if token A is a prefix of token B, then it
    # comes after token B in the list.
    Tokens.EQ,
    Tokens.LEQ,
    Tokens.GEQ,
    Tokens.LT,
    Tokens.GT,
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
    Tokens.UNIT_CONVERT,
    Tokens.ARRAY_OPEN,
    Tokens.ARRAY_CLOSE,
    Tokens.ARRAY_SEPARATOR,
    Tokens.ARRAY_CONDITION_SEP,
    Tokens.ELEMENT_OF,
    Tokens.INTERVAL_OPEN,
    Tokens.INTERVAL_CLOSE,
    Tokens.INTERVAL_SEPARATOR,
    Tokens.KW_SEPARATOR,
    Tokens.INSTANT,
]

ALPHA_TOKENS = set(t for t in CONST_TOKENS if t.isalpha())

class UnknownTokenError(Exception):
    def __init__(self, index):
        self.index = index

class BadNumberError(Exception):
    def __init__(self, index):
        self.index = index

class UnclosedStringError(Exception):
    def __init__(self, index):
        self.index = index

class UnclosedInstantError(Exception):
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
    if s[i] == "\"":
        return read_string(i, s)
    if s[i] == "#":
        return read_instant(i, s)
    if s[i].isnumeric() or s[i] == '.':
        return read_num_token(i, s)
    for t in CONST_TOKENS:
        if s.startswith(t, i) and (
                # Tokens that consist only of alphabetical
                # characters can potentially clash with
                # variable names, e.g. token 'in' with the
                # function 'int'. So need to  check if the
                # next character is alphabetical.
                t not in ALPHA_TOKENS
                or i+len(t)>=len(s)
                or not s[i+len(t)].isalpha()):
            return Token(t, i, i+len(t))
    if s[i].isalpha():
        m = VAR_REGEX.match(s, i)
        return Token(Tokens.VAR, m.start(), m.end(), name=m.group(0))
    return None

def read_string(i, s):
    j = i+1
    while j < len(s):
        if s[j] == "\\" and j+1 < len(s) and s[j+1] == "\"":
            j += 2
        elif s[j] == "\"":
            return Token(Tokens.STRING, i, j+1, value=s[i+1:j])
        else:
            j += 1
    raise UnclosedStringError(i)

def read_instant(i, s):
    j = i+1
    while j < len(s):
        if s[j] == "#":
            return Token(Tokens.INSTANT, i, j+1, value=s[i+1:j])
        j += 1
    raise UnclosedInstantError(i)

def read_num_token(i, s):
    m = NUM_REGEX.match(s, i)
    with_base = m.group(1)
    if with_base:
        base = 10
        raw_base = m.group(2)
        if raw_base:
            if "b" == raw_base: base = 2
            elif "o" == raw_base: base = 8
            elif "x" == raw_base: base = 16
        try:
            value = int(m.group(3), base=base)
        except ValueError:
            raise BadNumberError(i)
    else:
        raw_value = m.group(4)
        # Keep it as an integer if possible.
        if '.' in raw_value:
            value = float(raw_value)
        else:
            value = int(raw_value)
        if m.group(7):
            exponent = int(m.group(7)[1:])
            if exponent < 0:
                value *= frac(1, 10**-exponent)
            else:
                value *= 10**exponent
    return Token(Tokens.NUM, m.start(), m.end(), value=value)
