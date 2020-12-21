import re

NUM_REGEX = re.compile(r"([0-9]+\.?[0-9]*)|([0-9]*\.?[0-9]+)")
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
    VAR = 'var'
    NUM = 'num'

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
    Tokens.EXP
]

class BagOfTokens:
    def __init__(self, tokens):
        self.tokens = tokens
        self.ptr = 0

    def empty(self):
        return self.ptr >= len(self.tokens)
    
    def peak(self, *tags):
        return all(self.check_type(i, tag) for i, tag in enumerate(tags))

    def peak_any(self, *tags):
        return any(self.check_type(0, tag) for tag in tags)

    def check_type(self, i, t):
        return self.ptr+i < len(self.tokens) and t == self.tokens[self.ptr+i].tag

    def read(self, t):
        if not self.check_type(self.ptr, t):
            raise Exception(f"Expected token of type {t} but was {self.tokens[self.ptr].tag}")
        return self.read_next()

    def read_next(self):
        token = self.tokens[self.ptr]
        self.ptr += 1
        return token

    def expect(self, *tags):
        if not self.peak(*tags):
            raise Exception("Missing token(s): " + str(tags))
        self.ptr += len(tags)

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
    return BagOfTokens(tokens)

def skip_whitespace(i, s):
    while i < len(s) and s[i].isspace():
        i += 1
    return i

def read_token(i, s):
    read_fn = get_read_fn(i, s)
    return read_fn(i, s)

def get_read_fn(i, s):
    if s[i].isalpha():
        return read_var_token
    if s[i].isnumeric() or s[i] == '.':
        return read_num_token
    return read_const_token

def read_var_token(i, s):
    m = VAR_REGEX.match(s, i)
    return Token(Tokens.VAR, m.start(), m.end(), name=m.group(0))

def read_num_token(i, s):
    m = NUM_REGEX.match(s, i)
    raw_value = m.group(0)
    # Keep it as an integer if possible.
    if '.' in raw_value:
        value = float(raw_value)
    else:
        value = int(raw_value)
    return Token(Tokens.NUM, m.start(), m.end(), value=value)

def read_const_token(i, s):
    for t in CONST_TOKENS:
        if s.startswith(t, i):
            return Token(t, i, i+len(t))
    return None
