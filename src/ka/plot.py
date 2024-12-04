from .types import KaRuntimeError, is_true
from numbers import Number
import itertools

def plot(xs, ys, label=None,
         xlabel=None, ylabel=None,
         xlo=None, xhi=None, ylo=None, yhi=None,
         colour=None,
         marker=None, markercolour=None,
         grid=None, title=None,
         ylog=None, xlog=None,
         legend=None):
    import matplotlib.pyplot as plt
    if len(xs) != len(ys):
        raise KaRuntimeError("Tried to plot arrays of differing lengths.")
    if any(not isinstance(x, Number) for x in itertools.chain(xs, ys)):
        raise KaRuntimeError("Tried to plot a non-numerical value.")
    if xlo or ylo:
        plt.xlim(left=xlo, right=xhi)
    if ylo or yhi:
        plt.ylim(bottom=ylo, top=yhi)
    if grid and is_true(grid):
        plt.grid(linestyle="--")
    if xlog:
        plt.xscale("log")
    if ylog:
        plt.yscale("log")
    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    kws = dict(
        label=label,
        color=colour,
        marker=marker,
        markerfacecolor=markercolour,
        markeredgecolor=markercolour)
    plt.plot(xs, ys,
        **dict((k, v) for k, v in kws.items()
                      if v is not None))
    if legend:
        plt.legend()
    plt.show()
