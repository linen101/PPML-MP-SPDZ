#program.use_edabit(True)
program.set_bit_length(200)

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
    result = SC_fun.LTS(sint(a), sint(b), bit_length).reveal()
    print_ln('LTS=%s', result)

start_timer(1)
(a,b) = create_a_b()  
stop_timer(1)     

start_timer(2)
bench_mul(a,b)  
stop_timer(2)  

start_timer(3)
bench_square(a)  
stop_timer(3)  

#start_timer(4)
#bench_comp(a,b)  
#stop_timer(4)

start_timer(5)
a_values = create_a_values(size=100)  
stop_timer(5) 

"""    
for i in range(100):
    #a_values[i].reveal()
    print_ln('a is %s.', (a_values[i]).reveal())

start_timer(6)
#@for_range_opt(10)
#def _(i):
a_max = bench_argmax(a_values)  
stop_timer(6)
"""
start_timer(7)
bench_lts(a,b)  
stop_timer(7)  