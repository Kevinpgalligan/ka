import math
from ka.probability import (
    Binomial, Poisson, Geometric, Bernoulli,
    UniformInt, Exponential, Uniform, Gaussian,
    InvalidParameterException)

import pytest

def test_binomial():
    X = Binomial(5, .5)
    assert 0 == X.pmf(-1)
    assert 0 == X.pmf(6)
    assert 0 == X.cdf(-1)
    assert math.isclose(2.5, X.mean())
    assert math.isclose(0.3125, X.pmf(2))
    assert math.isclose(0.03125 + 0.15625 + 0.3125, X.cdf(2))
    assert 0 == X.cdf(-1)
    assert 1 == X.cdf(6)
    with pytest.raises(InvalidParameterException):
        Binomial(0, .5)
    with pytest.raises(InvalidParameterException):
        Binomial(1, -.1)
    with pytest.raises(InvalidParameterException):
        Binomial(1, 1.1)

def test_poisson():
    with pytest.raises(InvalidParameterException):
        Poisson(0)
    X = Poisson(5)
    assert 5 == X.mean()
    assert math.isclose(0.146223, X.pmf(6), abs_tol=1e-5)
    assert math.isclose(0.124652, X.cdf(2), abs_tol=1e-5)

def test_geometric():
    with pytest.raises(InvalidParameterException):
        Geometric(-.1)
    with pytest.raises(InvalidParameterException):
        Geometric(1.1)
    X = Geometric(0.4)
    assert 0 == X.cdf(0)
    assert math.isclose(0.784, X.cdf(3), abs_tol=1e-3)
    assert math.isclose(0.784, X.pmf(1) + X.pmf(2) + X.pmf(3), abs_tol=1e-3)

def test_bernoulli():
    with pytest.raises(InvalidParameterException):
        Bernoulli(-.1)
    with pytest.raises(InvalidParameterException):
        Bernoulli(1.1)
    X = Bernoulli(.3)
    assert 1-.3 == X.pmf(0)
    assert .3 == X.pmf(1)
    assert 0 == X.pmf(2)
    assert 1 == X.cdf(1)
    assert 1-.3 == X.cdf(0)
    assert 0 == X.cdf(-1)
    assert .3 == X.mean()

def test_uniform_int():
    with pytest.raises(InvalidParameterException):
        UniformInt(4, 3)
    X = UniformInt(5, 7)
    assert math.isclose(6, X.mean())
    assert math.isclose(1/3, X.pmf(5))
    assert math.isclose(1/3, X.pmf(7))
    assert math.isclose(2/3, X.cdf(6))
    assert 0 == X.cdf(4)
    assert 1 == X.cdf(7)
    assert 0 == X.pmf(4)
    assert 0 == X.pmf(8)

def test_exponential():
    with pytest.raises(InvalidParameterException):
        Exponential(0)
    X = Exponential(3)
    assert math.isclose(1/3, X.mean())
    assert math.isclose(0.950213, X.cdf(1), abs_tol=1e-5)
    assert 0 == X.cdf(-.1)
    
def test_uniform():
    with pytest.raises(InvalidParameterException):
        Uniform(1.1, 1)
    X = Uniform(0, 1)
    assert math.isclose(.5, X.mean())
    assert math.isclose(.5, X.cdf(.5))
    assert 0 == X.cdf(-.01)
    assert 1 == X.cdf(1.01)

def test_gaussian():
    with pytest.raises(InvalidParameterException):
        Gaussian(0, 0)
    X = Gaussian(2, 1.5)
    assert 2 == X.mean()
    assert math.isclose(0.252492537546923, X.cdf(1))
