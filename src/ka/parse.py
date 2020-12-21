import operator
import treelib

from .tokens import Tokens

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

def pretty_print_parse_tree(root):
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

def parse_tokens(tokens):
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
