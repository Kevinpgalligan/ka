import math
import operator
import re
import treelib
import argparse

NUM_REGEX = re.compile(r"([0-9]+\.?[0-9]*)|([0-9]*\.?[0-9]+)")
VAR_REGEX = re.compile(r"[a-zA-Z][_a-zA-Z0-9]*")

CONSTANTS = {
    "e": math.e,
    "pi": math.pi
}

#### TOKENISATION STUFF

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

def tokenise(s):
    i = 0
    i = skip_whitespace(i, s)
    tokens = []
    while i < len(s):
        token = read_token(i, s)
        i = skip_whitespace(token.end_index_excl, s)
        tokens.append(token)
    return Tokens(tokens)

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
    raise Exception(f"Couldn't match {s[i]} with a known token!")

#### PARSE TREE STUFF

def just_return_label(label, *args):
    return label

class ParseNode:
    def __init__(self, label="", children=None, eval_fn=just_return_label):
        """label: self-explanatory. Not necessarily a string.
        children: child nodes.
        eval_fn: used to evaluate the node."""
        self.label = label
        self.children = children if children else []
        self.eval_fn = eval_fn

    def eval(self, environment):
        child_values =  [child.eval(environment) for child in self.children]
        return self.eval_fn(self.label, child_values, environment)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "".join(["ParseNode[", str(self.label), "]"])

def value_node(v):
    return ParseNode(label=v)

def variable_node(name):
    def eval_fn(label, _, environment):
        if name in environment:
            return environment[name]
        raise Exception("Unknown variable: " + name)
    return ParseNode(label=name, eval_fn=eval_fn)

def operator_node(label, op, children):
    def eval_fn(_, child_values, *_s):
        return op(*child_values)
    return ParseNode(label=label, children=children, eval_fn=eval_fn)

def assignment_node(name, expression):
    def eval_fn(_, child_values, environment):
        environment[name] = child_values[0]
        return child_values[0]
    return ParseNode(label=name+"=", children=[expression], eval_fn=eval_fn)

def statements_node(children):
    def eval_fn(_, child_values, *_s):
        return child_values[-1] if child_values else None
    return ParseNode(children=children, eval_fn=eval_fn)

#### ACTUAL PARSING STUFF

def parse_math_expression(s):
    tokens = tokenise(s)
    return parse_statements(tokens)

def parse_statements(t):
    statements = []
    while not t.empty():
        statements.append(parse_statement(t))
        if not t.empty():
            t.expect(Tokens.STATEMENT_SEPARATOR)
    return statements_node(statements)

def parse_statement(t):
    if t.peak(Tokens.VAR, Tokens.ASSIGNMENT_OP):
        return parse_assignment(t)
    return parse_expression(t)

def parse_assignment(t):
    var_token = t.read(Tokens.VAR)
    t.expect(Tokens.ASSIGNMENT_OP)
    return assignment_node(var_token.meta('name'), parse_expression(t))

def parse_expression(t):
    return parse_sum(t)

def parse_sum(t):
    return parse_binary_op(t, parse_factor, [Tokens.PLUS, Tokens.MINUS])

def parse_binary_op(t, parse_operand, operator_tokens):
    left = parse_operand(t)
    if t.peak_any(*operator_tokens):
        token = t.read_next()
        return operator_node(token.tag,
                             token_to_op(token),
                             [left, parse_binary_op(t, parse_operand, operator_tokens)])
    return left

def parse_factor(t):
    return parse_binary_op(t, parse_term, [Tokens.MULT, Tokens.DIV, Tokens.MOD])

def parse_term(t):
    return parse_binary_op(t, parse_value, [Tokens.EXP])

def parse_value(t):
    token = t.read_next()
    if token.tag == Tokens.LBRACKET:
        expression = parse_expression(t)
        t.expect(Tokens.RBRACKET)
        return expression
    elif token.tag == Tokens.NUM:
        return value_node(token.meta('value'))
    elif token.tag == Tokens.VAR:
        return variable_node(token.meta('name'))
    else:
        raise Exception("Unexpected token: " + token.tag)

def token_to_op(token):
    return {
        Tokens.PLUS: operator.add,
        Tokens.MINUS: operator.sub,
        Tokens.MULT: operator.mul,
        Tokens.DIV: operator.truediv,
        Tokens.MOD: operator.mod,
        Tokens.EXP: operator.pow
    }[token.tag]

def pretty_print_parse_tree(root):
    tree = treelib.Tree()
    stack = [(root, None, 0)]
    i = 0
    while stack:
        node, parent, node_index = stack.pop()
        # y u makin' me do this, treelib.
        tree.create_node(str(node.label), i, parent=parent, data=node_index)
        for child_index, child in enumerate(node.children):
            stack.append((child, i, child_index))
        i += 1
    tree.show(key=lambda node: node.data)

def main():
    parser = argparse.ArgumentParser(description="A toy calculator language.")
    parser.add_argument("x", help="The statements to evaluate.")
    parser.add_argument("--print-tree",
                        action="store_true",
                        help="Whether to print the parse tree instead of evaluating it.")
    args = parser.parse_args()
    parse_tree = parse_math_expression(args.x)
    if args.print_tree:
        pretty_print_parse_tree(parse_tree)
    else:
        print(parse_tree.eval(CONSTANTS.copy()))

if __name__ == "__main__":
    main()
