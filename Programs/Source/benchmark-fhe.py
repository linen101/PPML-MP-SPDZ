program.use_edabit(True)
program.set_bit_length(200)

import itertools
import random
import math
#import numpy as np
from Compiler import types, library, instructions
from Compiler import comparison, util
from Programs.Source import random_matrix

#fprecision = 32
#sfix.set_precision(f=fprecision)

def create_a_b():
    a = types.sint.get_random(size=1)
    b = types.sint.get_random(size=1)
    return (a,b)

def bench_mul(a,b):
    a*b

def bench_square(a):
    types.sint.square(a)
    
def bench_comp(a,b):
    a < b

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