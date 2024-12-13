import math
from .types import Combinatoric, IntRange

def separate_kwargs(kwargs, selected_keys):
    selected = {}
    other = {}
    for k, v in kwargs.items():
        if k in selected_keys:
            selected[k] = v
        else:
            other[k] = v
    return selected, other

def _g(d, k, default=None):
    return d.get(k, default)

def choose(n, k):
    if k > n or n < 0 or k < 0:
        return 0

    M = n + 1
    nterms = min(k, n - k)

    numerator = 1
    denominator = 1
    for j in range(1, nterms + 1):
        numerator *= M - j
        denominator *= j

    return numerator // denominator

def lazy_choose(n, k):
    if k > n or n < 0 or k < 0:
        return 0
    # n!/(k!(n-k)!)
    return Combinatoric(
        ns=[] if n < 2 else [IntRange(2, n)],
        ds=[r for r in [IntRange(2, k), IntRange(2, n-k)]
            if not r.is_empty()])

def factorial(n):
    result = 1
    if n < 2:
        return result
    for k in range(2, n+1):
        result *= k
    return result

def lazy_factorial(n):
    if n < 2:
        return 1
    return Combinatoric(ns=[IntRange(2, n)])

# Copied someone's port of scipy's C implementation.
# See:
#  https://stackoverflow.com/questions/42381244/pure-python-inverse-error-function
def erfinv(z):
    if z < -1 or z > 1:
        raise ValueError("`z` must be between -1 and 1 inclusive")
    if z == 0:
        return 0
    if z == 1:
        return math.inf
    if z == -1:
    	return -math.inf
    return ndtri((z + 1) / 2.0) / math.sqrt(2)

def ndtri(y):
	P0 = [
		-5.99633501014107895267E1,
		9.80010754185999661536E1,
		-5.66762857469070293439E1,
		1.39312609387279679503E1,
		-1.23916583867381258016E0,
	]

	Q0 = [
		1.95448858338141759834E0,
		4.67627912898881538453E0,
		8.63602421390890590575E1,
		-2.25462687854119370527E2,
		2.00260212380060660359E2,
		-8.20372256168333339912E1,
		1.59056225126211695515E1,
		-1.18331621121330003142E0,
	]

	P1 = [
		4.05544892305962419923E0,
		3.15251094599893866154E1,
		5.71628192246421288162E1,
		4.40805073893200834700E1,
		1.46849561928858024014E1,
		2.18663306850790267539E0,
		-1.40256079171354495875E-1,
		-3.50424626827848203418E-2,
		-8.57456785154685413611E-4,
	]

	Q1 = [
		1.57799883256466749731E1,
		4.53907635128879210584E1,
		4.13172038254672030440E1,
		1.50425385692907503408E1,
		2.50464946208309415979E0,
		-1.42182922854787788574E-1,
		-3.80806407691578277194E-2,
		-9.33259480895457427372E-4,
	]

	P2 = [
		3.23774891776946035970E0,
		6.91522889068984211695E0,
		3.93881025292474443415E0,
		1.33303460815807542389E0,
		2.01485389549179081538E-1,
		1.23716634817820021358E-2,
		3.01581553508235416007E-4,
		2.65806974686737550832E-6,
		6.23974539184983293730E-9,
	]

	Q2 = [
		6.02427039364742014255E0,
		3.67983563856160859403E0,
		1.37702099489081330271E0,
		2.16236993594496635890E-1,
		1.34204006088543189037E-2,
		3.28014464682127739104E-4,
		2.89247864745380683936E-6,
		6.79019408009981274425E-9,
	]

	s2pi = 2.50662827463100050242
	code = 1

	if y > (1.0 - 0.13533528323661269189):
		y = 1.0 - y
		code = 0

	if y > 0.13533528323661269189:
		y = y - 0.5
		y2 = y * y
		x = y + y * (y2 * polevl(y2, P0, 4) / p1evl(y2, Q0, 8))
		x = x * s2pi
		return x

	x = math.sqrt(-2.0 * math.log(y))
	x0 = x - math.log(x) / x

	z = 1.0 / x
	if x < 8.0:
		x1 = z * polevl(z, P1, 8) / p1evl(z, Q1, 8)
	else:
		x1 = z * polevl(z, P2, 8) / p1evl(z, Q2, 8)

	x = x0 - x1
	if code != 0:
		x = -x

	return x

def polevl(x, coefs, N):
    ans = 0
    power = len(coefs) - 1
    for coef in coefs:
        ans += coef * x**power
        power -= 1
    return ans

def p1evl(x, coefs, N):
    return polevl(x, [1] + coefs, N)
