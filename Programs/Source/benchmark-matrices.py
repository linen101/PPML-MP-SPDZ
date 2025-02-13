#program.use_edabit(True)

import itertools
import random
import math
from Compiler import types, library, instructions
from Compiler import comparison, util
from Compiler import ml
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
def generate_random_shared_matrix(n, d, alpha, beta):
    # Set global precision for sfix...
    matrix_a = types.Matrix(n, d, types.sfix)
    @for_range_opt(n)
    def _(i):
        @for_range_opt(d)
        def _(j):
            value = random.uniform(alpha, beta)
            value_sfix =  types.sfix(value)
            matrix_a[i][j] = value_sfix
    return matrix_a  

###   Generate a diagonal matrix with random uniform values for a player ###
def generate_epsilon_matrix(n, alpha, beta):
    matrix_a = types.Matrix(n, n, types.cfix)
    for i in range(n):
        for j in range(n):
            if i == j:  # Only set diagonal elements
                value = random.uniform(alpha, beta)
                value_cfix = types.cfix(1- value)
                matrix_a[i][j] = value_cfix
            else:
                matrix_a[i][j] = types.cfix(0- value)  # Off-diagonal elements set to zero
    return matrix_a


def mat_prod(a, b, n, d, alpha, beta):
    c =  a.direct_mul(b)
    return c

def check_inverse(dataset_length, matrix_I, epsilon):
    matrix_result = types.Matrix(dataset_length, dataset_length, types.cfix)
    @for_range_opt(dataset_length)
    def _(i):
        @for_range_opt(dataset_length)
        def _(j):
            result = (matrix_I[i][j] < epsilon )  
            result.reveal()
           
dataset_length = 100000
features = 100

matrix_a = generate_random_shared_matrix(features, features, alpha =0,   beta=1)
matrix_b = generate_random_shared_matrix(features, 1, alpha=0, beta=1)

start_timer(1)
C = mat_prod(a=matrix_a, b=matrix_b, n=features, d=features, alpha=0, beta=1)    
stop_timer(1)
"""
matrix_r = generate_random_shared_matrix(dataset_length, 1, alpha=0, beta=1)

start_timer(1)
@for_range_opt(dataset_length)
def _(i):
    abs(matrix_r[i][0])
stop_timer(1)

"""
D = generate_random_shared_matrix(n=features, d=features, alpha=0.0001, beta=0.00001) 
#E = generate_epsilon_matrix(n=features, alpha=0.0001, beta=0.00001) 
start_timer(2)
check_inverse(dataset_length=features, matrix_I=D, epsilon=0.00001)
stop_timer(2)
                           
    


#A = generate_random_shared_matrix(n=features, d=features, alpha=0, beta=1)
#Ainv =  ml.mr(A, 6)   