program.use_edabit(True)

program.set_security(40)
program.set_bit_length(63)

import itertools
import random
import math
#import numpy as np
from Compiler import types, library, instructions
from Compiler import comparison, util, ml
from Programs.Source import random_matrix
from Compiler import SC_fun

# Set the bit length based on edabit
bit_length = program.bit_length

n = 1000

res = sint.Array(n)

n_threads = 1

l = 1

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

print('%d comparison in %d threads and %d rounds' % (n, n_threads, l))



#fprecision = 32
#sfix.set_precision(f=fprecision)

def create_a_b():
    a = types.sint.get_random(size=1)
    b = types.sint.get_random(size=1)
    return (a,b)

def create_a_values(size):
    a = types.sint.get_random(size=100)
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

def bench_lts(a,b):
    """Computes the Least Than Secret (LTS) of two values and prints the result."""
    result = SC_fun.LTS(sint(a), sint(b), bit_length)


start_timer(1)
(a,b) = create_a_b()  
stop_timer(1)     
"""
start_timer(2)
bench_mul(a,b)  
stop_timer(2)  

start_timer(3)
bench_square(a)  
stop_timer(3)  

start_timer(4)
bench_comp(a,b)  
stop_timer(4)
"""
start_timer(5)
a_values = create_a_values(size=100)  
stop_timer(5) 

"""    
for i in range(100):
    #a_values[i].reveal()
    print_ln('a is %s.', (a_values[i]).reveal())

start_timer(6)
@for_range_opt(10)
def _(i):
    a_max = bench_argmax(a_values)  
stop_timer(6)
"""
#start_timer(7)
#bench_lts(a,b)  
#stop_timer(7)  

start_timer(8)
@multithread(n_threads, n)
def _(base, m):
    @for_range(l)
    def _(i):
        (ml.argmax(a_values)).store_in_mem(base)
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