import readline
from fractions import Fraction as frac
import sys

from .tokens import (tokenise, UnknownTokenError, BadNumberError,
    UnclosedStringError, UnclosedInstantError)
from .parse import parse_tokens, ParsingError
from .eval import eval_parse_tree, EvalError, EvalEnvironment, EvalModes
from .types import Quantity, Array, Combinatoric, KaRuntimeError
from .functions import (FUNCTIONS, UnknownFunctionError,
    UnknownKeywordError, BadTypeKeywordError,
    NoMatchingFunctionSignatureError, IncompatibleQuantitiesError,
    make_sig_printable, ExitKaSignal, FUNCTION_DOCUMENTATION,
    FunctionArgError, resolve_combinatoric)
from .plot import Plot
from .units import UNITS, PREFIXES, lookup_unit
from .probability import InvalidParameterException
from .config import ConfigProperties
import ka.config

PROMPT = ">>> "
INTERPRETER_COMMAND_PREFIX = "%"
KA_VERSION = "1.2"

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
        print(format_unit_info(unit))

def format_unit_info(unit):
    return "\n".join([
        f"Name: {unit.singular_name}", 
        f"Plural name: {unit.plural_name}",
        f"Symbol: {unit.symbol}",
        f"Quantities: " + ", ".join(unit.quantities),
        f"Base units: {unit.quantity_vector.prettified()}",
        f"Multiplier: {unit.multiple}",
        f"Offset: {unit.offset}",
    ])

def print_functions():
    print(get_functions_string())

def get_functions_string():
    return ", ".join(name for name in FUNCTIONS.keys())

def print_function_info(name):
    if name not in FUNCTIONS:
        print("Unknown function.")
    else:
        print(format_function_info(name))

def format_function_info(name):
    des = (FUNCTION_DOCUMENTATION[name]
           if name in FUNCTION_DOCUMENTATION
           else DEFAULT_DOCSTRING)
    sigs = list(map(lambda h: h.sig, FUNCTIONS[name]))
    return "\n".join([
        f"Name: {name}",
        f"Description: {des}",
        "Accepted argument types: ",
        "\n".join("  " + make_sig_printable(sig)
                  for sig in sigs)
    ])

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

def default_unit_format(qv):
    return qv.prettified()

def execute(s, env=None, out=sys.stdout,
            errout=sys.stderr, reraise_signals=False,
            # This is a hacky, C-like way of passing
            # back the actual result of the computation, since
            # normally the function returns an integer status
            # code.
            result_box=None,
            brackets_for_frac=False,
            assigned_box=None,
            post_display_action_box=None,
            unit_format_fn=default_unit_format):
    if env is None:
        env = EvalEnvironment()
    try:
        tokens = tokenise(s)
    except UnknownTokenError as e:
        error("Unknown token!", e.index, s, errout)
        return 1
    except BadNumberError as e:
        error("Bad number! (Probably mixing number bases).", e.index, s, errout)
        return 1
    except UnclosedStringError as e:
        error("String is missing closing delimiter.", e.index, s, errout)
        return 1
    except UnclosedInstantError as e:
        error("Instant/date is missing closing delimiter.", e.index, s, errout)
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
    except KaRuntimeError as e:
        print_err(errout, e.msg)
        return 1
    statements = parse_tree.children
    if len(statements)>0:
        last_one = statements[-1]
        if last_one.eval_mode == EvalModes.ASSIGNMENT and assigned_box is not None:
            assigned_box.value = last_one.value
    try:
        result = eval_parse_tree(parse_tree, env)
        reduced = reduce_result(result)
        if reduced is None:
            print(file=out)
        else:
            display_result(reduced, out,
                           brackets_for_frac=brackets_for_frac,
                           unit_format_fn=unit_format_fn)
            if result_box is not None:
                result_box.value = reduced
        if isinstance(result, Plot):
            def post_display_action():
                execute_plot(result, errout)
            if post_display_action_box is None:
                post_display_action()
            else:
                post_display_action_box.value = post_display_action
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
    except KaRuntimeError as e:
        print_err(errout, e.msg)
        return 1
    except UnknownFunctionError as e:
        print_err(errout, f"Unknown function: '{e.name}'")
        global FUNCTIONS
        alternatives = find_close_matches(e.name, FUNCTIONS.keys())
        if alternatives:
            print_err(errout, "  You may have meant:", ", ".join(alternatives))
        return 1
    except UnknownKeywordError as e:
        kw_args = e.fn_header.sig.kw_args
        print_err(errout,
            f"Function '{e.fn_header.name}' received unknown keyword: '{e.kw_name}'")
        print_err(errout, "Available keywords:",
            ", ".join(kw_args.keys()) if len(kw_args) > 0 else "<none>")
        return 1
    except BadTypeKeywordError as e:
        print_err(errout,
            f"Function '{e.fn_header.name}' received type '{e.kw_value}' for keyword '{e.kw_name}', but expected '{e.expected_type}'.")
        return 1
    except InvalidParameterException as e:
        print_err(errout, e.msg)
        return 1
    except NoMatchingFunctionSignatureError as e:
        print_err(errout, f"Function '{e.name}' does not accept {printable_signature(e.attempted_signature)}.")
        print_err(errout, "It does accept:")
        for sig in e.actual_signatures:
            print_err(errout, "   ", sig)
        return 1
    except IncompatibleQuantitiesError as e:
        print_err(errout, "Tried to combine two incompatible quantities.")
        print_err(errout, "The first is a quantity of:")
        print_err(errout, "   ", e.qv1.prettified())
        print_err(errout, "The second is a quantity of:")
        print_err(errout, "   ", e.qv2.prettified())
        return 1
    except FunctionArgError as e:
        print_err(errout, e.msg)
        return 1

def reduce_result(r):
    if isinstance(r, Plot):
        return None
    if isinstance(r, Combinatoric):
        return resolve_combinatoric(r)
    return r

def execute_plot(plot, errout):
    try:
        plot.do()
    except Exception as e:
        print_err(errout, "Error in call to plotting lib...")
        print_err(errout, e)

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

def display_result(r, out, brackets_for_frac=False, newline=True, unit_format_fn=default_unit_format):
    # This is nightmare code. Oh well.
    newline_args = dict() if newline else dict(end="")
    if isinstance(r, Quantity):
        if isinstance(r.mag, frac):
            print(prettify_frac(r.mag, brackets=brackets_for_frac),
                  unit_format_fn(r.qv),
                  end="",
                  file=out)
        else:
            print(r.mag, unit_format_fn(r.qv), end="", file=out)
        if isinstance(r.mag, frac):
            print("    (" + str(float(r.mag)) + " " + unit_format_fn(r.qv) + ")", end="", file=out)
        print(file=out, **newline_args)
    elif isinstance(r, frac):
        print(prettify_frac(r),
              "    (" + str(precisionify_float(float(r))) + ")",
              file=out,
              **newline_args)
    elif isinstance(r, float):
        print(precisionify_float(r), file=out, **newline_args)
    elif isinstance(r, Array):
        print("{", file=out, end="")
        for i, e in enumerate(r.contents):
            print(stringify_result(e), file=out, end="")
            if i < len(r)-1:
                print(", ", file=out, end="")
        print("}", file=out, **newline_args)
    else:
        print(r, file=out, **newline_args)


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
    elif isinstance(r, Array):
        return ("{"
                + ", ".join(stringify_result(x,
                                             brackets_for_frac=brackets_for_frac) 
                            for x in r.contents)
                + "}")
    elif isinstance(r, str):
        return "\"" + r + "\""
    return str(r)

def precisionify_float(f):
    fstring = "{:." + str(ka.config.get(ConfigProperties.PRECISION)) + "g}"
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
