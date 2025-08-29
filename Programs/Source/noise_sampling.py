#import numpy as np
import itertools
import random
import math

from Compiler import types, library, instructions
from Compiler import comparison, util
from Compiler import ml
from Programs.Source import random_matrix

from Programs.Source.trip import *
import sys

#from Sampling.primitives_mpc import distributed_sample, bitwise_sample

def binomial_sample(s, n):
    k = 2*s
    noise = types.Array(n, types.sfix)
    s1=sint(0)
    s2=sint(0)
    MemValue(s1)
    MemValue(s2)
    # stretch refers to the standard deviation
    @for_range_opt(n)
    def _(i):
        @for_range_opt(k)
        def _(j):
            s1.update(s1 + types.sint.get_random_bit())
            s2.update(s2 - types.sint.get_random_bit())
            noise[i] = s1 + s2    
    noise[:] = noise[:]/ 2**8
    return noise;

n=500
m=2
start_timer(2)
print_ln("parties:%s", m)
print_ln("samples:%s", n)
test = sint(1)
print_ln("test: %s", test.reveal())
noise = binomial_sample(s=500, n=n)
print_ln("noise: %s", noise.reveal())

#noised_y = bitwise_sample(n=n, s=1, mechanism='gauss', binary=0, num_party=m) # use bitwise sampling
stop_timer(2)