from .types import KaRuntimeError

def plot(xs, ys):
    import matplotlib.pyplot as plt
    if len(xs) != len(ys):
        raise KaRuntimeError("Tried to plot arrays of differing lengths.")
    plt.plot(xs, ys)
    plt.show()
