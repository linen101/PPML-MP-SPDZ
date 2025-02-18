#program.use_edabit(True)
#import matplotlib.pyplot as plt

import itertools
import random
import math
import sys
from Compiler import types, library, instructions
from Compiler import comparison, util
from Compiler import ml
from Programs.Source import random_matrix
fprecision = 16
types.sfix.set_precision(f=fprecision)
types.cfix.set_precision(f=fprecision)

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

def generate_personal_matrix(player, n, d, alpha, beta):
    matrix_a = types.personal(player, types.Matrix(n, d, types.cfix))
    @for_range_opt(n)
    def _(i):
        @for_range_opt(d)
        def _(j):
            # not secure for benchmark puproses only
            value = random.uniform(alpha, beta)
            value_cfix =  types.cfix(value)
            matrix_a[i][j] = value_cfix
    return matrix_a  


def share_personal_matrix(matrix_a, n, d):
    matrix_sa = sfix.Matrix(n, d)
    matrix_sa[:] = sfix(matrix_a[:])
    return matrix_sa  

###   test generation of random uniform array  ###
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


def mat_prod(a, b):
    c =  a.direct_mul(b)
    return c

def check_inverse(dataset_length, matrix_I, epsilon):
    @for_range_opt(dataset_length)
    def _(i):
        @for_range_opt(dataset_length)
        def _(j):
            result = (matrix_I[i][j] < epsilon )  
            result.reveal()
"""
# input size           
dataset_length = 100000
features = 10

# A: [dxd], B: [dx1]
matrix_a = generate_random_shared_matrix(features, features, alpha =0,   beta=1)
matrix_b = generate_random_shared_matrix(features, 1, alpha=0, beta=1)
"""

def bench_helen(m, d_list, alpha, beta):
    i=1
    for d in d_list: 
        start_timer(i) 
        for p in range(m):        
            # D: [dxn], C:[dxd] ,  A: [dxd], B: [dx1], H: [dxd]
            for i in range(8):
                matrix_d = generate_personal_matrix(p, d, d, alpha, beta)        
                # measure overhead of sharing personal matrix
                matrix_sd = share_personal_matrix(matrix_d, d, d)
            for i in range(2):
                matrix_a = generate_personal_matrix(p, 1, d, alpha, beta)
                matrix_b = generate_personal_matrix(p, d, 1, alpha, beta)
                matrix_sa = share_personal_matrix(matrix_a, 1, d)  
                matrix_sb = share_personal_matrix(matrix_b, d, 1) 
            for i in range(16):
                mat_prod(matrix_sa , matrix_sb)
            for i in range(2):
                mat_prod(matrix_sd , matrix_sb) 
            for i in range(2):
                check_inverse(d, matrix_sd, 1)      
        stop_timer(i)
        i = i + 1
        
# Default values (optional)
alpha=0
beta=1
m = 2  # Number of parties
d_list = [25, 50, 75, 100]
# Parse arguments only when running (not compiling)
   
if len(sys.argv) > 2 and sys.argv[2].isdigit():  
    m = int(sys.argv[2])
    print_ln(" m  =  %s", m)
   
if len(sys.argv) > 3:  
    d_list = list(map(int, sys.argv[3].split(",")))
    print_ln("d_list = %s", d_list)

# Call functions with the parsed parameters

bench_helen(m, d_list, alpha, beta)

#a = sfix.get_random(alpha, beta, 100)
#a = types.personal(0, cfix.get_random(alpha, beta, 100))
#ssfix(a)
"""
mat = types.personal(0, cfix.Matrix(5, 5))
mat[0][0] = cfix(1)
mat[4][4] = cfix(999)

# Where the magic happens
sfix_mat = sfix.Matrix(5,5)
sfix_mat[:] = sfix(mat[:])

sfix_mat.print_reveal_nested()
"""