
program.use_edabit(True)
program.use_trunc_pr
import itertools
import random
import math
import numpy as np
from Compiler import types, library, instructions
from Compiler import comparison, util
from Programs.Source import random_matrix

fprecision = 16
sfix.set_precision(f=fprecision)

# personal(player, Array(n, cint))
# Array value known to one player. 
# Supports operations with public values and personal values known to the same player. 
# Can be used with print_ln_to(). It is possible to convert to secret types like sint.
# Parameters: 
    # player – player (int)
    # # value – cleartext value (cint, cfix, cfloat) or array thereof
# Local computations on each party with types.personal have some limitations.
# In MP-SPDZ it is not possible to run  codes, which contain control flows, locally only on some parties owning the associating data.. 
# !!! The general design is that the high-level code runs in sync on all parties !!! 
# Operations on personal values are run "dryly" on parties where the value isn't present so it still fits the design. 
# You can think of the Python code running on the arithmetic black-box that MPC provides whereas the actual protocol runs on the C++ level.


###   test generation of random uniform array for a player ###
def generate_personal_array(player, length, alpha, beta):
    # Set global precision for sfix...
    array_a = types.personal(player, Array(length, types.cfix))
    @for_range_opt(length)
    def _(i):
        value = random.uniform(alpha, beta)
        value_cfix =  types.cfix(value)
        array_a[i] = value_cfix
    return array_a  

#n = 10;
#array_0 = generate_personal_array(0, n, 0, 1)
##############################################


#f = array_0[1] * array_0[0]
#g = sfix(f)
# reveal a secret shared value.
#print_ln('result %s', g.reveal())   
###############################################



def count_smaller_than_m_secretly( dataset, dataset_length, m):
    # element-wise comparison (A < m)
    comparison_results = types.Array(dataset_length, types.sint)
    count = types.sint(0)
    @for_range_opt(dataset_length)
    def _(i):
        nonlocal count
        count += (types.sint(dataset[i]) < cfix(m)) + sint(0)
    return count    


def count_greater_than_m_secretly( dataset, dataset_length, m):
    # element-wise comparison (A < m)
    comparison_results = types.Array(dataset_length, types.sint)
    count = types.sint(0)
    @for_range_opt(dataset_length)
    def _(i):
        c = (sint(dataset[i]) > m) + sint(0)
        nonlocal count
        count = count + c
    return count    

n = 10000;
array_0 = generate_personal_array(player=0, length=n, alpha=0, beta=1)

m = cfix(0.37)
q = count_greater_than_m_secretly( dataset=array_0, dataset_length=n, m=m)

print_ln("number of elements greater than %s is: %s", m, q.reveal())
##############################################