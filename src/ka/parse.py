from .tokens import Tokens
from .types import simplify_number, instant_from_iso
from .eval import EvalModes

class ParseNode:
    def __init__(self,
                 value=None,
                 label="",
                 children=None,
                 eval_mode=EvalModes.LEAF,
                 meta=None,
                 eval_children=True):
        self.value = value
        self.label = label
        self.children = children if children else []
        self.eval_mode = eval_mode
        self.meta = meta if meta else dict()
        self.eval_children = eval_children

    def __repr__(self):
        return str(self)

    def __str__(self):
        return ("ParseNode("
            + ",".join([str(self.label)]
            + list(map(str, self.children)))
            + ")")

def funcall_node(name, children):
    return ParseNode(label=name,
                     value=name,
                     children=children,
                     eval_mode=EvalModes.FUNCALL)

def quantity_node(term, unit_sig):
    return ParseNode(label=str(unit_sig),
                     children=[term],
                     eval_mode=EvalModes.QUANTITY,
                     value=unit_sig)

def unit_convert_node(sum_node, unit_sig):
    return ParseNode(label=Tokens.UNIT_CONVERT + " " + str(unit_sig),
                     children=[sum_node],
                     eval_mode=EvalModes.CONVERT_UNIT,
                     value=unit_sig)

FORWARD_OPS = [Tokens.LT, Tokens.LEQ]
BACKWARD_OPS = [Tokens.GT, Tokens.GEQ]

def make_comparison_node(terms, ops):
    back = any(op in BACKWARD_OPS for op in ops)
    if back and not any(op in FORWARD_OPS for op in ops):
        # Flip the operators to reduce function duplication. We only
        # implement the forward-facing comparison operators.
        i = 0
        while i < len(ops):
            if ops[i] in BACKWARD_OPS:
                op_index = BACKWARD_OPS.index(ops[i])
                ops[i] = FORWARD_OPS[op_index]
            i += 1
        ops.reverse()
        terms.reverse()
    label = "_".join(ops)
    return ParseNode(label=label,
                     value=label,
                     children=terms,
                     eval_mode=EvalModes.FUNCALL)

def make_array_node(elements):
    label = "{...}"
    return ParseNode(label=label,
                     value=label,
                     children=elements,
                     eval_mode=EvalModes.ARRAY)

def make_array_with_condition_node(body, clauses):
    assignments = []
    conditions = []
    for clause in clauses:
        if "generator" in clause.meta:
            assignments.append(clause)
        else:
            conditions.append(clause)
    label = "{...}"
    # This is getting ridiculously hacky. Should just have different
    # implementations of ParseNode and they each have their own
    # version of eval().
    return ParseNode(label=label,
                     value=label,
                     children=[body]+assignments+conditions,
                     eval_mode=EvalModes.ARRAY_WITH_CONDITION,
                     meta=dict(num_assignments=len(assignments)),
                     eval_children=False)

def make_generator_node(name, array_expr):
    array_expr.meta["generator"] = True
    array_expr.meta["name"] = name
    return array_expr

def parse_tokens(tokens):
    return parse_statements(BagOfTokens(tokens))

class BagOfTokens:
    def __init__(self, tokens):
        self.tokens = tokens
        self.ptr = 0

    def empty(self):
        return self.ptr >= len(self.tokens)

    def next_is(self, tag):
        return self.next_are(tag)

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

def parse_unit_convert(t, sum_node):
    t.read(Tokens.UNIT_CONVERT)
    unit_signature = parse_unit_signature(t)
    return unit_convert_node(sum_node, unit_signature)

def parse_assignment(t):
    var_token = t.read(Tokens.VAR)
    t.read(Tokens.ASSIGNMENT_OP)
    name = var_token.meta('name')
    return ParseNode(label=name,
                     value=name,
                     children=[parse_expression(t)],
                     eval_mode=EvalModes.ASSIGNMENT)

def parse_expression(t):
    comparison_node = parse_comparison(t)
    if t.next_are(Tokens.UNIT_CONVERT):
        return parse_unit_convert(t, comparison_node)
    return comparison_node

def parse_comparison(t):
    terms = [parse_sum(t)]
    comparison_ops = []
    for _ in range(2):
        if not t.next_is_one_of(Tokens.EQ, Tokens.NEQ, Tokens.LT, Tokens.GT,
                                Tokens.LEQ, Tokens.GEQ, Tokens.ASSIGNMENT_OP,
                                Tokens.ELEMENT_OF):
            break
        comparison_ops.append(t.read_any())
        terms.append(parse_sum(t))
    if not comparison_ops:
        return terms[0]
    return make_comparison_node(terms,
                                list(map(lambda t: t.tag, comparison_ops)))

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
    if t.next_is(Tokens.STRING):
        return parse_string(t)
    if t.next_is(Tokens.INSTANT):
        return parse_instant(t)
    if t.next_is(Tokens.ARRAY_OPEN):
        return parse_array(t)
    if t.next_is(Tokens.INTERVAL_OPEN):
        return parse_interval(t)
    return parse_maybe_range(t)

def parse_string(t):
    s = t.read(Tokens.STRING).meta("value")
    return ParseNode(label="\"" + s + "\"", value=s)

def parse_instant(t):
    raw_inst = t.read(Tokens.INSTANT).meta("value")
    return ParseNode(label=raw_inst, value=instant_from_iso(raw_inst))

def parse_array(t):
    t.read(Tokens.ARRAY_OPEN)
    xs = []
    if not t.next_are(Tokens.ARRAY_CLOSE):
        xs.append(parse_expression(t))
        if t.next_are(Tokens.ARRAY_CONDITION_SEP):
            t.read_any()
            body = xs[0]
            clauses = [parse_clause(t)]
            while t.next_are(Tokens.ARRAY_SEPARATOR):
                t.read_any()
                clauses.append(parse_clause(t))
            t.read(Tokens.ARRAY_CLOSE)
            return make_array_with_condition_node(body, clauses)
        else:
            while t.next_are(Tokens.ARRAY_SEPARATOR):
                t.read_any()
                xs.append(parse_expression(t))
    t.read(Tokens.ARRAY_CLOSE)
    return make_array_node(xs)

def parse_clause(t):
    if t.next_are(Tokens.VAR, Tokens.ELEMENT_OF):
        var_token = t.read_any()
        t.read_any()
        name = var_token.meta('name')
        array_expr = parse_expression(t)
        return make_generator_node(name, array_expr)
    return parse_expression(t)

def parse_interval(t):
    t.read(Tokens.INTERVAL_OPEN)
    lo = parse_expression(t)
    t.read(Tokens.INTERVAL_SEP)
    hi = parse_expression(t)
    t.read(Tokens.INTERVAL_CLOSE)
    return funcall_node("interval", (lo, hi))

def parse_maybe_range(t):
    lo = parse_maybe_quantity(t)
    if t.next_is(Tokens.RANGE_SEPARATOR):
        t.read_any()
        hi = parse_maybe_quantity(t)
        return funcall_node("range", (lo, hi))
    return lo

def parse_maybe_quantity(t):
    term = parse_unitless_term(t)
    if t.next_is_one_of(Tokens.VAR):
        # It's a quantity! Which has a magnitude and
        # a unit signature.
        return quantity_node(term, parse_unit_signature(t))
    return term

def parse_unitless_term(t):
    if t.next_is_one_of(Tokens.PLUS, Tokens.MINUS):
        token = t.read_any()
        return funcall_node(token.tag, [parse_unsigned_term(t)])
    return parse_unsigned_term(t)

def parse_unsigned_term(t):
    term = parse_unsigned_term_without_factorial(t)
    if not t.next_is_one_of(Tokens.FACTORIAL):
        return term
    token = t.read_any()
    return funcall_node(token.tag, [term])

def parse_unsigned_term_without_factorial(t):
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
    v = t.read(Tokens.NUM).meta('value')
    return ParseNode(label=str(v), value=simplify_number(v))

def parse_function(t):
    name = t.read(Tokens.VAR).meta('name')
    t.read(Tokens.LBRACKET)
    node = funcall_node(name, parse_args(t))
    t.read(Tokens.RBRACKET)
    return node

def parse_args(t):
    return parse_positional_args(t) + parse_keyword_args(t)

def parse_positional_args(t):
    args = []
    while not t.next_is_one_of(Tokens.RBRACKET):
        if args:
            t.read(Tokens.FUNCTION_ARG_SEPARATOR)
        if t.next_are(Tokens.VAR, Tokens.KW_SEPARATOR):
            # Keyword argument, stop.
            break
        args.append(parse_expression(t))
    return args

def parse_keyword_args(t):
    kw_args = []
    while not t.next_is_one_of(Tokens.RBRACKET):
        if kw_args:
            t.read(Tokens.FUNCTION_ARG_SEPARATOR)
        name = t.read(Tokens.VAR).meta('name')
        t.read(Tokens.KW_SEPARATOR)
        kw_args.append(
            ParseNode(label=name,
                      children=[parse_expression(t)],
                      eval_mode=EvalModes.KEYWORD_ARG))
    return kw_args

def parse_variable(t):
    name = t.read(Tokens.VAR).meta('name')
    return ParseNode(label=name, value=name, eval_mode=EvalModes.VARIABLE)

def parse_unit_signature(t):
    units = parse_units(t)
    inverted_units = []
    if t.next_is_one_of(Tokens.UNIT_DIVIDE):
        t.read_any()
        inverted_units = parse_units(t)
    return UnitSignature(units, inverted_units)

class UnitSignature:
    def __init__(self, units, inverted_units):
        self.units = units
        self.inverted_units = inverted_units

    def __str__(self):  
        s = " ".join(f"{name}^{exp}" for name, exp in self.units) 
        if self.inverted_units:
            s += " | "
            s += " ".join(f"{name}^{exp}" for name, exp in self.inverted_units) 
        return s

    def __eq__(self, other):
        return (isinstance(other, UnitSignature)
                and self.units == other.units
                and self.inverted_units == other.inverted_units)

def parse_units(t):
    units = []
    while t.next_is_one_of(Tokens.VAR):
        unit_name = t.read_any().meta('name')
        exponent = 1
        if t.next_is_one_of(Tokens.EXP):
            t.read_any()
            exponent = parse_integer(t)
        units.append((unit_name, exponent))
    if not units:
        raise ParsingError("Missing units where expected.", t.ptr)
    return units

def parse_integer(t):
    sign = 1
    if t.next_is_one_of(Tokens.PLUS, Tokens.MINUS):
        token = t.read_any()
        if token.tag == Tokens.MINUS:
            sign = -1
    i = sign * t.read(Tokens.NUM).meta('value')
    if not isinstance(i, int):
        raise ParsingError(f"Expected an integer literal, got a {type(i)}.", t.ptr-1)
    return i
