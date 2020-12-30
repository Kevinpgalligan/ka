FUNCTIONS = {}

def register_function(f, name=None):
    global FUNCTIONS
    FUNCTIONS[name or f.__name__] = f

# TODO convert all these to standalone functions
def token_to_op(token):
    return wrap_binary_op({
        Tokens.PLUS: operator.add,
        Tokens.MINUS: operator.sub,
        Tokens.MULT: operator.mul,
        Tokens.DIV: divide,
        Tokens.MOD: operator.mod,
        Tokens.EXP: operator.pow
    }[token.tag])

def token_to_sign(token):
    return wrap_unary_op({
        Tokens.PLUS: operator.pos,
        Tokens.MINUS: operator.neg
    }[token.tag])


def wrap_binary_op(op):
    def new_op(n1, n2):
        n1, n2 = coerce(n1, n2)
        return number(op(n1.x, n2.x))
    return new_op

def wrap_unary_op(op):
    def new_op(n):
        return number(op(n.x))
    return new_op
