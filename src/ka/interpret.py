import readline
from fractions import Fraction as frac
import sys

from .tokens import tokenise, UnknownTokenError
from .parse import parse_tokens, ParsingError
from .eval import eval_parse_tree, EvalError, EvalEnvironment, EvalModes
from .types import Quantity
from .functions import (FUNCTIONS, UnknownFunctionError,
    NoMatchingFunctionSignatureError, IncompatibleQuantitiesError,
    make_sig_printable, ExitKaSignal, FUNCTION_DOCUMENTATION)
from .units import UNITS, PREFIXES, lookup_unit
import ka.config

PROMPT = ">>> "
INTERPRETER_COMMAND_PREFIX = "%"
KA_VERSION = "1.1"

ERROR_CONTEXT_SIZE = 5
INDENT = 2

DEFAULT_DOCSTRING = "n/a"

def interp_cmd(f, nargs, description):
    return InterpreterCommand(f, nargs, description)

class InterpreterCommand:
    def __init__(self, f, nargs, desc):
        self.f = f
        self.nargs = nargs
        self.desc = desc

    def execute(self, args):
        self.f(*args)

def interp_quit():
    raise ExitKaSignal()

def interp_help():
    for names, cmd in INTERPRETER_COMMANDS:
        if not isinstance(names, tuple):
            names = (names,)
        print(" ", ",".join(names) + ":", cmd.desc)

def print_units():
    print("\n".join(sorted(["  " + format_unit(unit) for unit in UNITS])))

def print_prefixes():
    for prefix in PREFIXES:
        print("  ", prefix.name_prefix + ",", prefix.symbol_prefix + ",", str(prefix.exponent) + ", base", prefix.base)

def format_unit(u):
    return f"{u.singular_name} ({u.symbol}) [{', '.join(u.quantities)}]"

def get_units_string():
    return ", ".join(format_unit(unit) for unit in UNITS)
    
def print_unit_info(name):
    unit = lookup_unit(name)
    if unit is None:
        print("Unknown unit.")
    else:
        print("                     Name:", unit.singular_name)
        print("              Plural name:", unit.plural_name)
        print("                   Symbol:", unit.symbol)
        print("               Quantities:", ", ".join(unit.quantities))
        print("    Base units equivalent:", unit.quantity_vector.prettified())
        print("  Magnitude in base units:", unit.multiple)
        print("   Offset from base units:", unit.offset)

def print_functions():
    print(get_functions_string())

def get_functions_string():
    return ", ".join(name for name in FUNCTIONS.keys())

def print_function_info(name):
    if name not in FUNCTIONS:
        print("Unknown function.")
    else:
        signatures = list(map(lambda x: x[1], FUNCTIONS[name]))
        print("                   Name:", name)
        print("          Documentation:", FUNCTION_DOCUMENTATION[name] if name in FUNCTION_DOCUMENTATION else DEFAULT_DOCSTRING)
        types_prompt = "Accepted argument types: "
        print(types_prompt, end="")
        for i, sig in enumerate(signatures):
            if i > 0:
                print(" "*len(types_prompt), end="")
            print("(" + ", ".join(make_sig_printable(sig)) + ")")

INTERPRETER_COMMANDS = [
    (("q", "quit"), interp_cmd(interp_quit, 0, "exit the interpreter")),
    (("h", "help"), interp_cmd(interp_help, 0, "display help")),
    (("u", "unit"), interp_cmd(print_unit_info, 1, "describe given unit")),
    (("us", "units"), interp_cmd(print_units, 0, "list all units")),
    (("f", "function"), interp_cmd(print_function_info, 1, "describe given function")),
    (("fs", "functions"), interp_cmd(print_functions, 0, "list all functions")),
]

def run_interpreter():
    env = EvalEnvironment()
    print("ka version", KA_VERSION)
    while True:
        try:
            s = input(PROMPT)
        except KeyboardInterrupt:
            print()
            break
        try:
            if s.startswith(INTERPRETER_COMMAND_PREFIX):
                execute_interpreter_command(s)
            else:
                execute(s, env, reraise_signals=True)
        except ExitKaSignal:
            break
        except KeyboardInterrupt:
            print()
            pass

def execute_interpreter_command(s):
    args = s[len(INTERPRETER_COMMAND_PREFIX):].split()
    cmd_name = args[0]
    args = args[1:]
    for names, cmd in INTERPRETER_COMMANDS:
        if (isinstance(names, tuple) and cmd_name in names) or (isinstance(names, str) and cmd_name == names):
            if cmd.nargs != len(args):
                print(f"Expected {cmd.nargs} arguments for command {names}, got {len(args)}.")
            else:
                cmd.execute(args)
            return
    print("Unknown interpreter command. You may have meant one of the following...")
    interp_help()

class ResultBox:
    def __init__(self):
        self.value = None

def execute(s, env=None, out=sys.stdout,
            errout=sys.stderr, reraise_signals=False,
            # This is a hacky, C-like way of passing
            # back the actual result of the computation, since
            # normally the function returns an integer status
            # code.
            result_box=None,
            brackets_for_frac=False,
            assigned_box=None):
    if env is None:
        env = EvalEnvironment()
    try:
        tokens = tokenise(s)
    except UnknownTokenError as e:
        error("Unknown token!", e.index, s, errout)
        return 1
    try:
        parse_tree = parse_tokens(tokens)
    except ParsingError as e:
        # 3 cases:
        #  a) there are no tokens, it's the empty string.
        #  b) we read all the tokens and then needed another one.
        #  c) unexpected token.
        if not tokens:
            index = 0
        elif e.token_index >= len(tokens):
            index = tokens[-1].end_index_excl
        else:
            index = tokens[e.token_index].begin_index_incl
        error(e.message, index, s, errout)
        return 1
    statements = parse_tree.children
    if len(statements)>0:
        last_one = statements[-1]
        if last_one.eval_mode == EvalModes.ASSIGNMENT and assigned_box is not None:
            assigned_box.value = last_one.value
    try:
        result = eval_parse_tree(parse_tree, env)
        if result is None:
            print(file=out)
        else:
            display_result(result, out, brackets_for_frac=brackets_for_frac)
            if result_box is not None:
                result_box.value = result
        return 0
    except ExitKaSignal as e:
        if reraise_signals:
            raise e
        return 0
    except KeyboardInterrupt as e:
        if reraise_signals:
            raise e
        print(file=out)
        return 0
    except EvalError as e:
        print_err(errout, e.message)
        return 1
    except UnknownFunctionError as e:
        print_err(errout, f"Unknown function: '{e.name}'")
        global FUNCTIONS
        alternatives = find_close_matches(e.name, FUNCTIONS.keys())
        if alternatives:
            print_err(errout, "  You may have meant:", ", ".join(alternatives))
        return 1
    except NoMatchingFunctionSignatureError as e:
        print_err(errout, f"Function '{e.name}' does not accept {printable_signature(e.attempted_signature)}.")
        print_err(errout, "It does accept:")
        for sig in e.actual_signatures:
            print_err(errout, "   ", printable_signature(sig))
        return 1
    except IncompatibleQuantitiesError as e:
        print_err(errout, "Tried to combine two incompatible quantities.")
        print_err(errout, "The first is a quantity of:")
        print_err(errout, "   ", e.qv1.prettified())
        print_err(errout, "The second is a quantity of:")
        print_err(errout, "   ", e.qv2.prettified())
        return 1

def print_err(errout, *msgs):
    print(*msgs, file=errout)

def find_close_matches(s, ss):
    return set(ss) & adjacent_strings([s])

def adjacent_strings(xs):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    final = set()
    for x in xs:
        final |= set([x[:i] + x[i+1:] for i in range(len(x))])
        final |= set([x[:i] + c + x[i:]
                     for c in alphabet
                     for i in range(len(x)+1)])
        final |= set([x[:i] + c + x[i+1:]
                      for c in alphabet
                      for i in range(len(x))])
    return final

def printable_signature(sig):
    return "(" + ", ".join(sig) + ")"

def error(msg, index, s, errout):
    error_lines = [msg]
    if s:
        context_low_index = max(0, index-ERROR_CONTEXT_SIZE)
        context_high_index = min(len(s), index+ERROR_CONTEXT_SIZE+1)
        left_fade = "" if context_low_index == 0 else "..."
        right_fade = "" if context_high_index == len(s) else "..."
        error_lines.append("")
        error_lines.append(
            " "*INDENT + left_fade + s[context_low_index:context_high_index] + right_fade)
        error_lines.append(
            " "*(INDENT+len(left_fade)+index-context_low_index) + "^")
    print("\n".join(error_lines), file=errout)

def display_result(r, out, brackets_for_frac=False):
    # This is nightmare code. Oh well.
    if isinstance(r, Quantity):
        if isinstance(r.mag, frac):
            print(prettify_frac(r.mag, brackets=brackets_for_frac),
                  r.qv.prettified(),
                  end="",
                  file=out)
        else:
            print(r.mag, r.qv.prettified(), end="", file=out)
        if isinstance(r.mag, frac):
            print("    (" + str(float(r.mag)) + " " + r.qv.prettified() + ")", end="", file=out)
        print(file=out)
    elif isinstance(r, frac):
        print(prettify_frac(r),
              "    (" + str(precisionify_float(float(r))) + ")",
              file=out)
    elif isinstance(r, float):
        print(precisionify_float(r), file=out)
    else:
        print(r, file=out)

def stringify_result(r, brackets_for_frac=False):
    """Stringify result so that it's syntactically valid, not just
    for display."""
    if isinstance(r, Quantity):
        return (stringify_result(r.mag, brackets_for_frac=brackets_for_frac)
                + " " + r.qv.prettified())
    elif isinstance(r, frac):
        s = str(r)
        if brackets_for_frac:
            s = "(" + s + ")"
        return s
    elif isinstance(r, float):
        return precisionify_float(r)
    return str(r)

def precisionify_float(f):
    fstring = "{:." + str(ka.config.PRECISION) + "g}"
    return fstring.format(f)

def prettify_frac(f, brackets=False):
    sign = 1 if f >= 0 else -1
    whole_part = abs(f.numerator) // abs(f.denominator)
    s = (f"{sign*whole_part} {abs(f) - whole_part}"
         if whole_part > 0
         else str(f))
    if brackets:
        s = "(" + s + ")"
    return s

