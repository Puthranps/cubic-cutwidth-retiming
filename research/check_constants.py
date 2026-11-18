"""Independent rational checks of the elementary margins in Section 7."""
from fractions import Fraction as F
from math import factorial


def r(x):
    return F(str(x))


def exp_bounds(x):
    """Bounds on exp(-x) by alternating Taylor on [0,1]."""
    scale = 1
    while x > 1:
        x /= 2
        scale *= 2
    low = sum((-x) ** k / factorial(k) for k in range(20))
    high = low + x**20 / factorial(20)
    assert low > 0
    return low**scale, high**scale


# sqrt(1/(2pi)) > .3988 follows from pi < 22/7.
assert r(.3988) ** 2 * F(44, 7) < 1
intervals = [
    (.03,1.285,.005), (.12,1.107,.025), (.12,1.423,.017),
    (.6,.3,.22), (.24,4.518,.000003), (.8,.4,.29)
]
prod = 1
for length, endpoint, lower in intervals:
    assert r(length)*r(.3988)*exp_bounds(r(endpoint)**2/2)[0] > r(lower)
    prod *= r(lower)
assert prod == r("4.06725e-13")

terms = [(2,.004,.0001), (4,.15,.017), (6,.33,.0412), (4,.64,.0757)]
# Monotonicity permits capping a very large exponent in an upper bound.
tail = sum(n*exp_bounds(min(F(100), r(m)**2/(2*r(s)**2)))[1]
           for n,m,s in terms)
assert tail < r("7.2e-14")
assert (prod-tail)/30 > r("1.11e-14")
pivotal_loss = 56*exp_bounds(r(.038)**2/(2*r(3.5)**2*r("5.5e-6")))[1]
assert pivotal_loss < r(.00125)
heavy_credit = r(.99)*r("1e-4")*r("5.5e-6")*r(.0165)/(88*F(44,7))
assert heavy_credit > r("1.6e-14")
print("all scalar checks passed")
