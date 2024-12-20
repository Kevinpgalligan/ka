from abc import ABC, abstractmethod
from numbers import Integral
import math
import random

from .utils import choose, factorial, erfinv

def unit():
    return random.random()

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

    @abstractmethod
    def sample(self):
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

    def sample(self):
        # Alternative approach: treat as a normal distribution
        # and round.
        c = 0
        for _ in range(self.n):
            if unit() < self.p:
                c += 1
        return c

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

    def sample(self):
        u = unit()
        k = 0
        p = 0
        while True:
            p += self.pmf(k)
            if p > u:
                break
            k += 1
        return k

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

    def sample(self):
        return math.ceil(math.log(1-unit())/math.log(1-self.p))

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

    def sample(self):
        return 1 if unit() < self.p else 0

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

    def sample(self):
        return math.floor(self.lo + unit()*(self.hi-self.lo+1))

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

    def sample(self):
        return -math.log(1-unit())/self.lam

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

    def sample(self):
        return self.lo + unit()*(self.hi - self.lo)

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

    def sample(self):
        return self.stddev*math.sqrt(2)*erfinv(2*unit()-1) + self.mu

    def __str__(self):
        return f"Gaussian(mean={self.mu}, stddev={self.stddev})"

class ComparisonOp:
    LEQ = "<="
    LT = "<"
    GT = ">"
    GEQ = ">="
    EQ = "="

class Event:
    def __init__(self, op, x, y):
        self.op = op
        self.x = x
        self.y = y

    def probability(self):
        return eval_probability(self.op, self.x, self.y)

    def __str__(self):
        return f"Event({self.x} {self.op} {self.y})"

class DoubleEvent:
    def __init__(self, op1, op2, x, y, z):
        self.op1 = op1
        self.op2 = op2
        self.x = x
        self.y = y
        self.z = z

    def probability(self):
        x_adjusted = self.x
        if (isinstance(self.y, DiscreteRandomVariable)
                and self.op1 == ComparisonOp.LEQ):
            x_adjusted -= 1
        p1 = eval_probability(ComparisonOp.LEQ, self.y, x_adjusted)
        p2 = eval_probability(self.op2, self.y, self.z)
        return max(p2 - p1, 0)

    def __str__(self):
        return f"Event({self.x} {self.op1} {self.y} {self.op2} {self.z})"

def eval_probability(op, left, right):
    # Japers, this is ugly. And there's bound to be
    # an off-by-1 error somewhere.
    if op == ComparisonOp.EQ:
        return left.pmf(right)
    if op == ComparisonOp.LEQ:
        if isinstance(left, RandomVariable):
            return left.cdf(right)
        if isinstance(right, DiscreteRandomVariable):
            return 1 - right.cdf(left-1)
        if isinstance(right, RandomVariable):
            return 1 - right.cdf(left)
    if op == ComparisonOp.LT:
        if isinstance(left, DiscreteRandomVariable):
            return left.cdf(right-1)
        if isinstance(left, RandomVariable):
            return left.cdf(right)
        if isinstance(right, RandomVariable):
            return 1 - right.cdf(left)
    raise Exception("Dunno how to evaluate the probability of this event! (This is a bug).")
