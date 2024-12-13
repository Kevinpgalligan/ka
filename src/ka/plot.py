from .types import KaRuntimeError, is_true
from .utils import _g, separate_kwargs
from numbers import Number
import itertools

class PlotType:
    pass

class PlotOptions(PlotType):
    def __init__(self, xlabel=None, ylabel=None,
                 xlo=None, xhi=None, ylo=None, yhi=None,
                 grid=None, title=None, ylog=None, xlog=None,
                 legend=None):
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xlo = xlo
        self.xhi = xhi
        self.grid = grid
        self.title = title
        self.ylog = ylog
        self.xlog = xlog
        self.legend = legend

    def pre_plot_do(self):
        if self.xlo or self.ylo:
            plt.xlim(left=self.xlo, right=self.xhi)
        if self.ylo or self.yhi:
            plt.ylim(bottom=self.ylo, top=self.yhi)
        if self.grid and is_true(self.grid):
            plt.grid(linestyle="--")
        if self.xlog:
            plt.xscale("log")
        if self.ylog:
            plt.yscale("log")
        if self.title:
            plt.title(self.title)
        if self.xlabel:
            plt.xlabel(self.xlabel)
        if self.ylabel:
            plt.ylabel(self.ylabel)

    def post_plot_do(self):
        if self.legend:
            plt.legend()

class Plot(PlotType):
    def __init__(self, func, option_kwargs=None):
        self.func = func
        self.options = Options(**option_kwargs) if option_kwargs else None

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
    def do():
        load_pyplot()
        for o in options:
            o.pre_plot_do()
        for p in actual_plots:
            p.func()
        for o in options:
            o.post_plot_do()
        plt.show()
    return Plot(do)

def load_pyplot():
    import matplotlib.pyplot as plt

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
    return Plot(do, o)

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
        plt.plot(xs, ys, **only_not_none(params))
    return Plot(do, o)

def vline(x, colour=None, weight=None, style=None):
    def do():
        params = dict(
            color=colour,
            linewidth=weight,
            linestyle=style)
        plt.axhline(x, **only_not_none(params))
    return Plot(do)

def hline(y, colour=None, weight=None, style=None):
    def do():
        params = dict(
            color=colour,
            linewidth=weight,
            linestyle=style)
        plt.axhline(y, **only_not_none(params))
    return Plot(do)
    
def text(x, y, s, colour=None, size=None):
    def do():
        params = dict(
            color=colour,
            fontsize=fontsize)
        plt.text(x, y, s, **only_not_none(params))
    return Plot(do)
