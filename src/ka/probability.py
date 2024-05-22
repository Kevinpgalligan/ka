from abc import ABC, abstractmethod
from numbers import Integral
import math

from .utils import choose, factorial

class InvalidParameterException(Exception):
    def __init__(self, msg):
        self.msg = msg

class RandomVariable:
    @abstractmethod
    def cdf(self, x):
        pass

    @abstractmethod
    def mean(self):
        pass

class DiscreteRandomVariable(RandomVariable):
    @abstractmethod
    def pmf(self, x):
        pass

class Binomial(DiscreteRandomVariable):
    def __init__(self, n, p):
        if n <= 0:
            raise InvalidParameterException(f"Parameter n for Binomial distribution must be greater than 0, was {n}.")
        if p < 0 or p > 1:
            raise InvalidParameterException(f"Parameter p for Binomial distribution must be between 0 and 1, was {p}.")
        self.n = n
        self.p = p

    def cdf(self, x):
        return sum(self.pmf(k) for k in range(x+1))

    def pmf(self, x):
        if x < 0 or x > self.n:
            return 0
        return choose(self.n, x) * self.p**x * (1-self.p)**(self.n-x)

    def mean(self):
        return self.n * self.p

    def __str__(self):
        return f"Binomial(n={self.n}, p={self.p})"

class Poisson(DiscreteRandomVariable):
    def __init__(self, mu):
        if mu <= 0:
            raise InvalidParameterException(f"Parameter mu for Poisson distribution must be greater than 0, was {mu}.")
        self.mu = mu

    def cdf(self, x):
        return math.exp(-self.mu) * sum(self.mu**j / factorial(j) for j in range(x+1))

    def pmf(self, x):
        return self.mu**x * math.exp(-self.mu) / factorial(x)

    def mean(self):
        return self.mu

    def __str__(self):
        return f"Poisson(rate={self.mu})"

class Geometric(DiscreteRandomVariable):
    def __init__(self, p):
        if p < 0 or p > 1:
            raise InvalidParameterException(f"Parameter p for Geometric distribution must be between 0 and 1, was {p}.")
        self.p = p

    def cdf(self, x):
        if x < 1:
            return 0
        return 1 - (1-self.p)**x

    def pmf(self, x):
        if x < 1:
            return 0
        return (1-self.p)**(x-1) * self.p

    def mean(self):
        return 1/self.p

    def __str__(self):
        return f"Geometric(p={self.p})"

class Bernoulli(DiscreteRandomVariable):
    def __init__(self, p):
        if p < 0 or p > 1:
            raise InvalidParameterException(f"Parameter p for Bernoulli distribution must be between 0 and 1, was {p}.")
        self.p = p

    def cdf(self, x):
        if x == 1: return 1
        if x == 0: return 1 - self.p
        else: return 0

    def pmf(self, x):
        if x == 1: return self.p
        if x == 0: return 1 - self.p
        else: return 0

    def mean(self):
        return self.p

    def __str__(self):
        return f"Bernoulli(p={self.p})"


class UniformInt(DiscreteRandomVariable):
    def __init__(self, lo, hi):
        if lo > hi:
            raise InvalidParameterException(
                f"Lower bound must be less than or equal to upper bound for UniformInt distribution. (Was: {lo} > {hi}).")
        self.lo = lo
        self.hi = hi

    def cdf(self, x):
        if x < self.lo:
            return 0
        if x >= self.hi:
            return 1
        return (x-self.lo+1)/(self.hi-self.lo+1)

    def pmf(self, x):
        if x < self.lo or x > self.hi:
            return 0
        return 1/(self.hi-self.lo+1)

    def mean(self):
        return self.lo + (self.hi - self.lo)/2

    def __str__(self):
        return f"UniformInt(lo={self.lo}, hi={self.hi})"

class Exponential(RandomVariable):
    def __init__(self, lam):
        if lam <= 0:
            raise InvalidParameterException(
                f"Rate parameter must be greater than 0 for exponential distribution, was: {lam}.")
        self.lam = lam

    def cdf(self, x):
        if x < 0:
            return 0
        return 1-math.exp(-self.lam * x)

    def mean(self):
        return 1/self.lam

    def __str__(self):
        return f"Exponential(rate={self.lam})"

class Uniform(RandomVariable):
    def __init__(self, lo, hi):
        if lo > hi:
            raise InvalidParameterException(
                f"Uniform random variable requires lower bound to be less than or equal to upper bound, was: {lo} > {hi}.")
        self.lo = lo
        self.hi = hi

    def cdf(self, x):
        if x < self.lo: return 0
        if x >= self.hi: return 1
        return (x-self.lo)/(self.hi-self.lo)

    def mean(self):
        return self.lo + (self.hi-self.lo)/2

    def __str__(self):
        return f"Uniform(lo={self.lo}, hi={self.hi})"

class Gaussian(RandomVariable):
    def __init__(self, mu, stddev):
        if stddev <= 0:
            raise InvalidParameterException(
                f"Gaussian random variable requires positive standard deviation, was: {stddev}.")
        self.mu = mu
        self.stddev = stddev

    def cdf(self, x):
        return (1/2)*(1 + math.erf((x - self.mu)/(self.stddev*math.sqrt(2))))

    def mean(self):
        return self.mu

    def __str__(self):
        return f"Gaussian(mean={self.mu}, stddev={self.stddev})"
