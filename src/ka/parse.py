from .tokens import Tokens
from .types import number
from .eval import EvalModes

class ParseNode:
    def __init__(self, label="", children=None, eval_mode=EvalModes.LABEL_IS_VALUE):
        self.label = label
        self.children = children if children else []
        self.eval_mode = eval_mode

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "".join(["ParseNode[", str(self.label), "]"])

def pretty_print_parse_tree(root):
    # This is the only place we use treelib, and the
    # import adds noticeable delay. So only import when
    # needed.
    import treelib
    tree = treelib.Tree()
    stack = [(root, None, 0)]
    i = 0
    while stack:
        node, parent, node_index = stack.pop()
        # y u makin' me store the order of child nodes, treelib.
        tree.create_node(str(node.label), i, parent=parent, data=node_index)
        for child_index, child in enumerate(node.children):
            stack.append((child, i, child_index))
        i += 1
    tree.show(key=lambda node: node.data)

def funcall_node(name, children):
    return ParseNode(label=name, children=children, eval_mode=EvalModes.FUNCALL)

def parse_tokens(tokens):
    return parse_statements(BagOfTokens(tokens))

class BagOfTokens:
    def __init__(self, tokens):
        self.tokens = tokens
        self.ptr = 0

    def empty(self):
        return self.ptr >= len(self.tokens)

    def next_are(self, *tags):
        return all(self.check_type(i, tag) for i, tag in enumerate(tags))

    def next_is_one_of(self, *tags):
        return any(self.check_type(0, tag) for tag in tags)

    def check_type(self, i, t):
        return self.ptr+i < len(self.tokens) and t == self.tokens[self.ptr+i].tag

    def read(self, tag):
        token = self._read_single_token(f"Expected '{tag}' but reached end.")
        if token.tag != tag:
            raise ParsingError(f"Expected '{tag}' but got '{token.tag}'.",
                               # Subtract 1 because the read advanced the pointer.
                               self.ptr-1)
        return token

    def read_any(self):
        return self._read_single_token("Reached end unexpectedly.")

    def _read_single_token(self, msg):
        if self.ptr >= len(self.tokens):
            raise ParsingError(msg, self.ptr)
        token = self.tokens[self.ptr]
        self.ptr += 1
        return token

class ParsingError(Exception):
    def __init__(self, message, token_index):
        self.message = message
        self.token_index = token_index

def parse_statements(t):
    statements = []
    while not t.empty():
        statements.append(parse_statement(t))
        if not t.empty():
            t.read(Tokens.STATEMENT_SEPARATOR)
    return ParseNode(children=statements, eval_mode=EvalModes.STATEMENTS)

def parse_statement(t):
    if t.next_are(Tokens.VAR, Tokens.ASSIGNMENT_OP):
        return parse_assignment(t)
    return parse_expression(t)

def parse_assignment(t):
    var_token = t.read(Tokens.VAR)
    t.read(Tokens.ASSIGNMENT_OP)
    return ParseNode(label=var_token.meta('name')+"=",
                     children=[parse_expression(t)],
                     eval_mode=EvalModes.ASSIGNMENT)

def parse_expression(t):
    return parse_sum(t)

def parse_sum(t):
    return parse_binary_op(t, parse_product, [Tokens.PLUS, Tokens.MINUS])

def parse_binary_op(t, parse_operand, operator_tokens):
    left = parse_operand(t)
    while t.next_is_one_of(*operator_tokens):
        token = t.read_any()
        # Ensuring that all operators are left-associative.
        left = funcall_node(token.tag, [left, parse_operand(t)])
    return left

def parse_product(t):
    return parse_binary_op(t, parse_factor, [Tokens.MULT, Tokens.DIV, Tokens.MOD])

def parse_factor(t):
    return parse_binary_op(t, parse_term, [Tokens.EXP])

def parse_term(t):
    if t.next_is_one_of(Tokens.PLUS, Tokens.MINUS):
        token = t.read_any()
        return funcall_node(token.tag, [parse_unsigned_term(t)])
    return parse_unsigned_term(t)

def parse_unsigned_term(t):
    if t.next_is_one_of(Tokens.LBRACKET):
        t.read(Tokens.LBRACKET)
        expression = parse_expression(t)
        t.read(Tokens.RBRACKET)
        return expression
    elif t.next_is_one_of(Tokens.NUM):
        return parse_number(t)
    elif t.next_are(Tokens.VAR, Tokens.LBRACKET):
        return parse_function(t)
    elif t.next_is_one_of(Tokens.VAR):
        return parse_variable(t)
    else:
        raise ParsingError("Unexpected token.", t.ptr)

def parse_number(t):
    return ParseNode(label=number(t.read(Tokens.NUM).meta('value')),
                     eval_mode=EvalModes.LABEL_IS_VALUE)

def parse_function(t):
    name = t.read(Tokens.VAR).meta('name')
    t.read(Tokens.LBRACKET)
    node = funcall_node(name, parse_args(t))
    t.read(Tokens.RBRACKET)
    return node

def parse_args(t):
    args = []
    while not t.next_is_one_of(Tokens.RBRACKET):
        if args:
            t.read(Tokens.FUNCTION_ARG_SEPARATOR)
        args.append(parse_expression(t))
    return args

def parse_variable(t):
    return ParseNode(label=t.read(Tokens.VAR).meta('name'),
                     eval_mode=EvalModes.VARIABLE)
