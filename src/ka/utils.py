def choose(n, k):
	# Yoinked this directly from the scipy source, since it is
	# slow to import scipy just for this.
	# Credit:
	# https://github.com/scipy/scipy/blob/main/scipy/special/_comb.pyx
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

def factorial(n):
	result = 1
	if n < 2:
		return result
	for k in range(2, n+1):
		result *= k
	return result
