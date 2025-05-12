#program.use_edabit(True)

program.set_security(40)
program.set_bit_length(32)

import itertools
import random
import math
#import numpy as np
from Compiler import types, library, instructions
from Compiler import comparison, util, ml
from Compiler.util import is_zero, tree_reduce
from Programs.Source import random_matrix
from Compiler import SC_fun

# Set the bit length based on edabit
bit_length = program.bit_length

# argmax to be computed in parallel depending on the depth of the tree
d1 = 100
d2 = 20
d3 = 40
d4 = 80

n_threads = 1

# number of rounds estimated for a computation
# propably not needed
l = 1

# number of computations
n = 10

# result
res = sint.Array(n)

try:
    n_threads = int(program.args[2])
except:
    pass

try:
    n = int(program.args[3])
except:
    pass

try:
    l = int(program.args[4])
except:
    pass

print('%d-lengthed vectors for argmax in %d threads' % (n, n_threads))



fprecision = 32
sfix.set_precision(f=fprecision)

def argmax(x):
    """ Compute index of maximum element.

    :param x: iterable
    :returns: sint or 0 if :py:obj:`x` has length 1
    """
    def op(a, b):
        #print_ln("index now is: %s", a[0])
        print_ln("a value now is: %s", a[1].reveal())
        #print_ln("a is: %s", a, print_secrets=True)
        comp = (a[1] > b[1])
        return comp.if_else(a[0], b[0]), comp.if_else(a[1], b[1])
    return tree_reduce(op, enumerate(x))[0]


def argmax_fraction(x):
    """ Compute index of maximum element.
    :param x: iterable contain pairs (x,x') where x is numerator and x' denumerator of a fraction
    x represented as a Matrix; x[:][0] nominators x[:][1] denominators
    a1/a2 >  b1/b2  (positive) =>  a1/a2 - b1/b2 > 0 => a1*b2 - a2*b1 > 0
    a[0][0] / a[1][0] >  b[0][0] / b[1][0] => a[0][0]*b[1][0] - a[1][0]*b[0][1] > 0
    :returns: sint or 0 if :py:obj:`x` has length 1
    """
    def op(a, b):
        # a and b are (index, [numerator, denominator])
        num_a, den_a = a[1]
        num_b, den_b = b[1]
        comp = (num_a * den_b > num_b * den_a)
        #print_ln("index now is: %s", a[0], print_secrets=True)
        #print_ln("a value now is: %s", a[1].reveal())
        #print_ln("b value now is: %s", b[1].reveal())
        #print_ln("a is: %s", a, print_secrets=True)
        return comp.if_else(a[0], b[0]), comp.if_else(a[1], b[1])
    return tree_reduce(op, enumerate(x))[0]

def create_a_b():
    a = types.sint.get_random(size=1)
    b = types.sint.get_random(size=1)
    return (a,b)

def create_a_values(size):
    a = types.sint.get_random_int(8,size=size)
    a = a.square() + 1
    return a

def bench_mul(a,b):
    a*b

def bench_square(a):
    types.sint.square(a)
    
def bench_comp(a,b):
    a < b
    
def bench_argmax(a_values):
    a_max = ml.argmax(a_values)  
    return a_max    

def bench_argmax_fraction(a_values):
    a_max = argmax_fraction(a_values)  
    return a_max   

def bench_lts(a,b):
    """Computes the Least Than Secret (LTS) of two values and prints the result."""
    result = SC_fun.LTS(sint(a), sint(b), bit_length)

a_tuple_array = sint.Matrix(2,n)
a_values = create_a_values(size=n)
b_values = create_a_values(size=n)  
a_tuple_array[0].assign(a_values)
a_tuple_array[1].assign(b_values)
a_tuple_array = a_tuple_array.transpose()

"""
start_timer(1)
(a,b) = create_a_b()  
stop_timer(1)     
start_timer(2)
bench_mul(a,b)  
stop_timer(2)  

start_timer(3)
bench_square(a)  
stop_timer(3)  

start_timer(4)
bench_comp(a,b)  
stop_timer(4)

# benchmark sharing of vector used for 1 argmax
start_timer(5)
a_array = sint.Array(100)
a_values = create_a_values(size=100)  
a_array.assign(a_values)
stop_timer(5) 
"""

""" TEST
a_tuple_array = sint.Matrix(3,2)
a_tuple_array[0][0] = sint(2)
a_tuple_array[0][1] = sint(4)
a_tuple_array[1][0] = sint(3)
a_tuple_array[1][1] = sint(9)
a_tuple_array[2][0] = sint(4)
a_tuple_array[2][1] = sint(12)
"""


"""

# benchmark the argmax operated over fraction values without truncation
start_timer(6)
@for_range_opt_multithread(n_threads, d1)
def _(i):
    #@for_range(l)
    #def _(i):
    a_max = bench_argmax_fraction(a_tuple_array)
@for_range_opt_multithread(n_threads, d2)
def _(i):
    #@for_range(l)
    #def _(i):
    a_max = bench_argmax_fraction(a_tuple_array)
@for_range_opt_multithread(n_threads, d3)
def _(i):
    #@for_range(l)
    #def _(i):
    a_max = bench_argmax_fraction(a_tuple_array)
@for_range_opt_multithread(n_threads, d4)
def _(i):
    #@for_range(l)
    #def _(i):
    a_max = bench_argmax_fraction(a_tuple_array)        
stop_timer(6)
"""
"""
a_max_fraction = a_max_fraction.reveal()
a_tuple_array=(a_tuple_array).reveal()
print_ln("argmax ind is: %s ", a_max_fraction)
print_ln("array is: %s ", a_tuple_array)
"""

""" TEST
a_array[0] = sint(1)
a_array[1] = sint(2)
a_array[2] = sint(4)
a_array[3] = sint(8)
a_array[4] = sint(10)
a_array[5] = sint(12)
a_array[6] = sint(11)
a_array[7] = sint(21)
a_array[8] = sint(111)
a_array[9] = sint(2)
"""
"""
# BENCHMARK the argmax operated over fraction values with truncation
#### TODO! ####
a_array = sfix.Array(n)

# benchmark fixed point division for the gini index
start_timer(7)
a_array[:] = a_tuple_array.get_column(0) / a_tuple_array.get_column(1)
stop_timer(7)

#a_array=(a_array).reveal()
#print_ln("array is: %s ", a_array)
#a_tuple_array=(a_tuple_array).reveal()
#print_ln("tuple array is: %s ", a_tuple_array)
"""

start_timer(8)
@for_range_opt_multithread(n_threads, d1)
def _(i):
    #@for_range(l)
    #def _(i):
    a_array[:] = a_tuple_array.get_column(0) / a_tuple_array.get_column(1)    
    a_max = bench_argmax(a_array)
@for_range_opt_multithread(n_threads, d2)
def _(i):
    #@for_range(l)
    #def _(i):
    a_array[:] = a_tuple_array.get_column(0) / a_tuple_array.get_column(1)    
    a_max = bench_argmax(a_array)
@for_range_opt_multithread(n_threads, d3)
def _(i):
    #@for_range(l)
    #def _(i):
    a_array[:] = a_tuple_array.get_column(0) / a_tuple_array.get_column(1)    
    a_max = bench_argmax(a_array)
@for_range_opt_multithread(n_threads, d4)
def _(i):
    #@for_range(l)
    #def _(i):
    a_array[:] = a_tuple_array.get_column(0) / a_tuple_array.get_column(1)    
    a_max = bench_argmax(a_array)       
stop_timer(8)

"""
start_timer(9)
@multithread(n_threads, n)
def _(base, m):
    @for_range(l)
    def _(i):
        (SC_fun.LTS(sint(a), sint(b), m)).store_in_mem(base)
stop_timer(9)
"""