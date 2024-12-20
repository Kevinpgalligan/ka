from .types import KaRuntimeError, is_true
from .utils import _g, separate_kwargs
from numbers import Number
import itertools

plt = None
ticker = None

class Plot:
    pass

class PlotOptions(Plot):
    def __init__(self, xlabel=None, ylabel=None,
                 xlo=None, xhi=None, ylo=None, yhi=None,
                 grid=None, title=None, ylog=None, xlog=None,
                 legend=None, xticks=None, yticks=None,
                 integer_x_ticks=None, integer_y_ticks=None):
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xlo = xlo
        self.xhi = xhi
        self.ylo = ylo
        self.yhi = yhi
        self.grid = grid
        self.title = title
        self.ylog = ylog
        self.xlog = xlog
        self.legend = legend
        self.xticks = xticks
        self.yticks = yticks
        self.integer_x_ticks = integer_x_ticks
        self.integer_y_ticks = integer_y_ticks

    def pre_plot_do(self):
        if self.xlo or self.ylo:
            plt.xlim(left=self.xlo, right=self.xhi)
        if self.ylo or self.yhi:
            plt.ylim(bottom=self.ylo, top=self.yhi)
        if self.xlog and is_true(self.xlog):
            plt.xscale("log")
        if self.ylog and is_true(self.ylog):
            plt.yscale("log")
        if self.grid and is_true(self.grid):
            plt.grid(linestyle="--")
        if self.title:
            plt.title(self.title)
        if self.xlabel:
            plt.xlabel(self.xlabel)
        if self.ylabel:
            plt.ylabel(self.ylabel)
        if self.xticks:
            plt.xticks(ticks=self.xticks,
                       labels=format_tick_labels(self.yticks))
        if self.yticks:
            plt.yticks(ticks=self.yticks,
                       labels=format_tick_labels(self.yticks))
        if self.integer_x_ticks and is_true(self.integer_x_ticks):
            set_integer_ticks(plt.gcf().gca().xaxis)
        if self.integer_y_ticks and is_true(self.integer_y_ticks):
            set_integer_ticks(plt.gcf().gca().yaxis)
        # So that gridlines appear behind plot. zorder wasn't working
        # for some reason.
        plt.gcf().gca().set_axisbelow(True)

    def post_plot_do(self):
        if self.legend and is_true(self.legend):
            plt.legend()

def format_tick_labels(ticks):
    return [(format_float_tick(x) if isinstance(x, float) else x)
            for x in ticks]   

TICK_MAX_DIGITS = 4

def format_float_tick(x):
    s = str(x)
    if "." not in s:
        return s
    i = s.index(".")
    num_digits = len(s)-i-1
    result = ("{:"
        + str(min(TICK_MAX_DIGITS, num_digits))
        + "f}").format(x).rstrip("0")
    return result + ("0" if result[-1]=="." else "")

def set_integer_ticks(ax):
    ax.set_major_locator(ticker.MaxNLocator(integer=True))

def options(**kwargs):
    return PlotOptions(**kwargs)

class PlotDrawing(Plot):
    def __init__(self, func, option_kwargs=None):
        self.func = func
        self.options = PlotOptions(**option_kwargs) if option_kwargs else None

    def do(self):
        load_pyplot()
        if self.options:
            self.options.pre_plot_do()
        self.func()
        if self.options:
            self.options.post_plot_do()
        plt.show()
            
def plot(*plots):
    options = []
    actual_plots = []
    for p in plots:
        if isinstance(p, PlotOptions):
            options.append(p)
        else:
            if p.options:
                options.append(p.options)
            actual_plots.append(p)
    load_pyplot()
    for o in options:
        o.pre_plot_do()
    for p in actual_plots:
        p.func()
    for o in options:
        o.post_plot_do()
    plt.show()

def load_pyplot():
    global plt, ticker
    if plt is None:
        import matplotlib.pyplot as plt
    if ticker is None:
        import matplotlib.ticker as ticker

def get_plt():
    global plt
    return plt

def line(xs, ys, **kwargs):
    check_all_numerical(xs)
    check_all_numerical(ys)
    sel, o = separate_kwargs(kwargs,
        ["label", "colour", "marker", "markercolour"])
    def do():
        params = dict(
            # This is ugly and error-prone.
            label=_g(sel, "label"),
            color=_g(sel, "colour"),
            marker=_g(sel, "marker"),
            markerfacecolor=_g(sel, "markercolour"),
            markeredgecolor=_g(sel, "markercolour"))
        plt.plot(xs, ys, **only_not_none(params))
    return PlotDrawing(do, o)

def only_not_none(dictionary):
    return dict((k, v) for k, v in dictionary.items()
                       if v is not None)

def check_all_numerical(xs):
    if any(not isinstance(x, Number) for x in xs):
        raise KaRuntimeError("Tried to plot a non-numerical value.")

def scatter(xs, ys, **kwargs):
    check_all_numerical(xs)
    check_all_numerical(ys)
    sel, o = separate_kwargs(kwargs,
        ["label", "colour", "marker", "size"])
    def do():
        params = dict(
            label=_g(sel, "label"),
            c=_g(sel, "colour"),
            marker=_g(sel, "marker"),
            s=_g(sel, "size"))
        plt.scatter(xs, ys, **only_not_none(params))
    return PlotDrawing(do, o)

def vline(x, colour=None, weight=None, style=None):
    def do():
        params = dict(
            color=colour,
            linewidth=weight,
            linestyle=style)
        plt.axvline(x, **only_not_none(params))
    return PlotDrawing(do)

def hline(y, colour=None, weight=None, style=None):
    def do():
        params = dict(
            color=colour,
            linewidth=weight,
            linestyle=style)
        plt.axhline(y, **only_not_none(params))
    return PlotDrawing(do)
    
def text(x, y, s, colour=None, size=None):
    def do():
        params = dict(
            color=colour,
            fontsize=size)
        plt.text(x, y, s, **only_not_none(params))
    return PlotDrawing(do)
