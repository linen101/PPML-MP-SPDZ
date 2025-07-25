#program.use_edabit(True)

program.set_security(40)

# set the bit length of the cleartext for the comparisons
#program.set_bit_length(64)
#program.set_bit_length(240)
# The length 106 is composed as follows: 
# assuming 64-bit integers, the difference used for comparison is a 65-bit integer, to which 40 bits are added for statistical masking, resulting in a 105 bits, 
# and it takes a 106-bit prime to able to contain all 105-bit numbers. Finally, the last line indicates which compile-time options would change the program.
# This supports the virtual machine in suggesting options that are compatible with the protocol implementation.
#program.use_trunc_pr = True

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
print_ln("%s-bit_length", bit_length)

# argmax to be computed collaboratively between the servers
# in parallel, on each tree level 
# e.g. if we assume 10 servers, each one training 10 decision trees\
    # then, on the first level d1 = 100 argmaxes can be computed independently, 
    # and on the second level d2=200 argmaxes in parallel, etc.. 
d1 = 100
d2 = 200 
d3 = 400
d4 = 800
d5 = 0
#d5 = 1600
d6 = 0
#d6 = 3200

n_threads = 48

# number of labels, 
# needed for the computation of gini
#t = 2
#t = 3
#t = 7
#t = 10

# number of elements in each vector\
    # this captures the different combinations of attributes and attribute values 
    # considered for possible split points.
# n = \alpha * \ceil[\sqrt(a)]    
n = 18              # t = 3
#n = 44             # t = 3
#n = 108            # t = 2
#n = 136            # t = 10
#n = 202            # t = 2
#n = 2048           # t = 7
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


#fprecision = 32
#sfix.set_precision(f=fprecision)

def create_tuple_array(n):
    """
    create a "tuple" array to encode sequence of gini indes values as fraction values
    a_tuple_array.get_column(0) : nominator
    a_tuple_array.get_column(1) : denominator
    Args:
        n (int): length of the array

    Returns:
        sint.Matrix(n,2): tuple array
    """
    a_tuple_array = sint.Matrix(2,n)
    a_values = create_a_values(size=n)
    b_values = create_a_values(size=n)  
    a_tuple_array[0].assign(a_values)
    a_tuple_array[1].assign(b_values)
    a_tuple_array = a_tuple_array.transpose()
    return a_tuple_array

def compute_gini(a,b,c,d,t):
    #c1 = sint(0)
    #d1 = sint(0)
    #gini = a^2 + b^2 - \sum_{over t} c^2 vals - \sum_{over t} d^2 vals
    @for_range_opt(t)
    def _(j):
        c.square()
        d.square()    
    gini = (a + b - c - d)
    return gini
    
def argmax(x):
    """ Compute index of maximum element.

    :param x: iterable
    :returns: sint or 0 if :py:obj:`x` has length 1
    """
    def op(a, b):
        #print_ln("index now is: %s", a[0])
        #print_ln("a value now is: %s", a[1].reveal())
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
        #comp = (num_a.TruncMul(den_b,32,32) > num_b.TruncMul(den_a,32,32))
        comp = (num_a * den_b ) > (num_b * den_a )
        #print_ln("index now is: %s", a[0], print_secrets=True)
        #print_ln("a value now is: %s", a[1].reveal())
        #print_ln("b value now is: %s", b[1].reveal())
        #print_ln("a is: %s", a, print_secrets=True)
        return comp.if_else(a[0], b[0]), comp.if_else(a[1], b[1])
    return tree_reduce(op, enumerate(x))[0]

def create_a_b():
    a = types.sint.get_random_int(120, size=1)
    b = types.sint.get_random_int(120, size=1)
    return (a,b)

def create_val():
    val = types.sint.get_random_int(120, size=1)
    val = val.square()
    return  MemValue(val)

def create_a_values(size):
    a = types.sint.get_random_int(120,size=size)
    a = a.square()
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
    
# create a "tuple" array to encode sequence of gini indes values as fraction values
#a_tuple_array = create_tuple_array(n)

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

a_array = sint.Array(n)
a_values = create_a_values(size=n)  
a_array.assign(a_values)

"""
# benchmark the argmax 
start_timer(6)
@for_range_opt_multithread(n_threads, d1)
def _(i):
    #@for_range(l)
    #def _(i):
    a_max = bench_argmax(a_array)
@for_range_opt_multithread(n_threads, d2)
def _(i):
    #@for_range(l)
    #def _(i):
    a_max = bench_argmax(a_array)
@for_range_opt_multithread(n_threads, d3)
def _(i):
    #@for_range(l)
    #def _(i):
    a_max = bench_argmax(a_array)
@for_range_opt_multithread(n_threads, d4)
def _(i):
    #@for_range(l)
    #def _(i):
    a_max = bench_argmax(a_array)  
@for_range_opt_multithread(n_threads, d5)
def _(i):
    #@for_range(l)
    #def _(i):
    a_max = bench_argmax(a_array) 
@for_range_opt_multithread(n_threads, d6)
def _(i):
    #@for_range(l)
    #def _(i):
    a_max = bench_argmax(a_array)               
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

# BENCHMARK the argmax operated over fraction values with truncation
"""
# benchmark fixed point division for the gini index
start_timer(7)
a_array[:] = a_tuple_array.get_column(0) / a_tuple_array.get_column(1)
stop_timer(7)

#a_array=(a_array).reveal()
#print_ln("array is: %s ", a_array)
#a_tuple_array=(a_tuple_array).reveal()
#print_ln("tuple array is: %s ", a_tuple_array)
"""

"""
If you need to use a Matrix with multi-threading, 
you need to allocate several matrices before-hand. 
You could allocate MM = sint.Tensor([10, 2, 2]) and 
then call M = MM[i]inside the loop.
"""
"""
start_timer(8)
MM  = sint.Tensor([d1, n])
@for_range_opt_multithread(n_threads, d1)
def _(i):
    #@for_range(l)
    #def _(i):
    M = MM[i]
    M[:] = a_tuple_array.get_column(0) / a_tuple_array.get_column(1)    
    a_max = bench_argmax(M)
MM  = sint.Tensor([d2, n])    
@for_range_opt_multithread(n_threads, d2)
def _(i):
    #@for_range(l)
    #def _(i):
    M = MM[i]    
    M[:] = a_tuple_array.get_column(0) / a_tuple_array.get_column(1)    
    a_max = bench_argmax(M)
MM  = sint.Tensor([d3, n])    
@for_range_opt_multithread(n_threads, d3)
def _(i):
    #@for_range(l)
    #def _(i):
    M = MM[i]    
    M[:] = a_tuple_array.get_column(0) / a_tuple_array.get_column(1)    
    a_max = bench_argmax(M)
MM  = sint.Tensor([d4, n])    
@for_range_opt_multithread(n_threads, d4)
def _(i):
    #@for_range(l)
    #def _(i):
    M = MM[i]    
    M[:] = a_tuple_array.get_column(0) / a_tuple_array.get_column(1)    
    a_max = bench_argmax(M)       
stop_timer(8)
"""

"""
start_timer(9)
@multithread(n_threads, n)
def _(base, m):
    @for_range(l)
    def _(i):
        (SC_fun.LTS(sint(a), sint(b), m)).store_in_mem(base)
stop_timer(9)
"""
# benchmark computation of GINI index with G' formula of overleaf
#(after FHE preprocessing: n as above )
#(without FHE, TOTAL IN MPC, n as below) 
"""
a = create_val()
b = create_val()
c = create_val()
d = create_val()
start_timer(10)
@for_range_opt_multithread(n_threads, d1*n)
def _(i):
    compute_gini(a,b,c,d,t)     
@for_range_opt_multithread(n_threads, d2*n)
def _(i):
    compute_gini(a,b,c,d,t)
@for_range_opt_multithread(n_threads, d3*n)
def _(i):
    compute_gini(a,b,c,d,t)
@for_range_opt_multithread(n_threads, d4*n)
def _(i):
    compute_gini(a,b,c,d,t)
@for_range_opt_multithread(n_threads, d5*n)
def _(i):
    compute_gini(a,b,c,d,t)
@for_range_opt_multithread(n_threads, d6*n)
def _(i):
    compute_gini(a,b,c,d,t)        
stop_timer(10)
"""
# benchmark computation of GINI index with G' formula of overleaf
#(without FHE, TOTAL IN MPC, n as below) 
a = create_val()
b = create_val()
#x = 25200  # iris
#x = 12600 # iris with subset of attributes
#x = 119119 # wine
x = 36652 # wine with subset of attributes

start_timer(11)
@for_range_opt_multithread(n_threads, d1*x)
def _(i):
    a*b
@for_range_opt_multithread(n_threads, d2*x)
def _(i):
    a*b
@for_range_opt_multithread(n_threads, d3*x)
def _(i):
    a*b
@for_range_opt_multithread(n_threads, d4*x)
def _(i):
    a*b
@for_range_opt_multithread(n_threads, d5*x)
def _(i):
    a*b
@for_range_opt_multithread(n_threads, d6*x)
def _(i):
    a*b        
stop_timer(11)