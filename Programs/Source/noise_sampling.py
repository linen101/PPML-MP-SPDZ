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

fprecision = 8
types.sfix.set_precision(f=fprecision)
types.cfix.set_precision(f=fprecision)
n=500
s=64
# Parse arguments only when running (not compiling)
   
if len(sys.argv) > 2 and sys.argv[2].isdigit():  
    n = int(sys.argv[2])
    print_ln(" n  =  %s", n)
   
if len(sys.argv) > 3 and sys.argv[3].isdigit():  
    s = int(sys.argv[3])
    print_ln("s = %s", s)
    

if len(sys.argv) > 4 and sys.argv[4].isdigit():  
    fprecision = int(sys.argv[4])
    print_ln("s = %s", fprecision)
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
    noise[:] = noise[:]/ 2**fprecision
    return noise;


start_timer(2)
print_ln("samples:%s", n)
noise = binomial_sample(s=s, n=n)
print_ln("noise: %s", noise.reveal())

#noised_y = bitwise_sample(n=n, s=1, mechanism='gauss', binary=0, num_party=m) # use bitwise sampling
stop_timer(2)