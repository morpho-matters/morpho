'''
This module defines the functions and constants that users
can use in the Morpho GUI like
sin, cos, tan, log, exp, sqrt, i, j, inf, real, imag,
conj, zeta.

It also implements a 2x2 matrix class so that linear
transformations can also be animated.
'''


import mpmath as mp
from math import *
from cmath import *
import numpy as np

# Special 2x2 matrix class for Morpho which can handle
# multiplication on a complex number by treating it as
# a 2D column vector.
class _Mat(np.matrix):

    def __mul__(self, other):
        if type(other) is _Mat:
            # Use the superclass to compute the matrix product
            return np.matrix.__mul__(self, other)
        else:
            Z = np.matrix([[other.real], [other.imag]])
            prod = np.matrix.__mul__(self, Z)
            return float(prod[0,0]) + float(prod[1,0])*1j

    # Convenience function: returns inverse of the mat
    @property
    def inv(self):
        return self**(-1)


# # Converts a numpy matrix into a Morpho _Mat
# # (Maybe unnecessary! numpy.matrix handles this somehow!)
# def matrix2Mat(matrix):
#     return Mat(matrix[0,0], matrix[0,1], matrix[1,0], matrix[1,1])

# This is the ACTUAL constructor for the 2x2 matrix class _Mat.
# Overriding the inherited __init__ from np.matrix turned out
# to be more complicated than I thought, so this was a workaround.
def Mat(x1=0, x2=0, y1=0, y2=0):
    return _Mat([[x1, x2], [y1, y2]])



### VARIOUS OTHER CONSTANTS AND FUNCTIONS ###

mat = MAT = Mat  # Any case works.
det = lambda M: np.linalg.det(M)  # For mats only
i = j = 1j
tau = 2*pi  # pi is wrong, apparently...
ln = log
inf = float("inf")
real = lambda s: s.real
Re = re = real
imag = lambda s: s.imag
Im = im = imag
arg = Arg = angle = Angle = Phase = phase
mod = lambda a,b: a % b
fact = factorial
conj = lambda s: s.conjugate()

# Standard Riemann Zeta function
def zeta(s):
    if s == 1: return nan
    else: return complex(mp.zeta(s))

# Treats s as a 2D vector and returns its lp-norm
def norm(s, p=2):
    if p == inf:
        return max(abs(Re(s)), abs(Im(s)))
    else:
        return (abs(Re(s))**p + abs(Im(s))**p)**(1/p)

# This function can be used to compress a standard grid
# into a disk (see animations/fun/flowers.mrm)
# More generally, this function squishes squares into
# their inscribed circles.
def disk(s):
    # return s/abs(s)*max(abs(Re(s)), abs(Im(s))) if s != 0 else 0
    return norm(s,inf)/abs(s) * s if s != 0 else 0
Disk = disk

# Inclusive range() function
def seq(start, end, step=1):
    return range(start, end+1, step)

# Computes the product of an iterable
# similar to how sum() computes the sum.
def prod(a):
    p = 1
    for n in a:
        p *= n
    return p

product = prod
