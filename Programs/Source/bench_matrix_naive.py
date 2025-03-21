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

def inverse_check(d_list, epsilon=0.0001):
    i=1
    for d in d_list:
        matrix_result = generate_epsilon_matrix(d=d, alpha=0, beta=0.00001)
        start_timer(i)
        @for_range_opt(d)
        def _(i):
            @for_range_opt(d_list)
            def _(j):
                result = (matrix_result[i][j] < epsilon )  
                result.reveal()
        stop_timer(i)
        i = i+1   

def range_check(n, q=0.1):
    i=20
    matrix_result = generate_random_shared_matrix(n, 1, alpha=0, beta=1)
    start_timer(i)
    @for_range_opt(n)
    def _(i):
        result = (matrix_result[i][j] < q )  
    stop_timer(i)
    i = i+1           
             
def model_inp_com(n, d_list, alpha, beta, m):
    i=10
    for d in d_list:
        # measure overhead of sharing personal matrix
        # has been computed in model_input_commitment
        matrix_sa = generate_random_shared_matrix(1, n, alpha, beta)
        matrix_sb = generate_random_shared_matrix(n, 1, alpha, beta)
        matrix_sc = generate_random_shared_matrix(1, d, alpha, beta)
        matrix_sd = generate_random_shared_matrix(d, 1, alpha, beta)
        # measure overhead of matrix mult in ADMM
        start_timer(i)
        @for_range_opt(m)
        def _(j):
            # measure overhead of d mult -> ADMM
            C = mat_prod(a=matrix_sa, b=matrix_sb)    
        
            D = mat_prod(a=matrix_sc, b=matrix_sd)    
                
        stop_timer(i)        
        i = i + 1

alpha =0
beta =1 
# Default values (optional)
m = 2  # Number of parties
n = 500  # Number of samples
d = 100  # Number of features
d_list = [25, 50, 75, 100, 150, 200, 300]
n_list = [1000, 10000, 100000, 1000000]

# Parse arguments only when running (not compiling)
   
if len(sys.argv) > 2 and sys.argv[2].isdigit():  
    m = int(sys.argv[2])
    print_ln(" m  =  %s", m)
   
if len(sys.argv) > 3 and sys.argv[3].isdigit():  
    n = int(sys.argv[3])
    n = n // m
    print_ln("n = %s", n)

if len(sys.argv) > 4 and sys.argv[4].isdigit():  
    d = int(sys.argv[4])
    print_ln("d = %s", d)
   
if len(sys.argv) > 5:  
    d_list = list(map(int, sys.argv[5].split(",")))
    print_ln("d_list = %s", d_list)

if len(sys.argv) > 6:  
    n_list = list(map(int, (sys.argv[6]).split(",")))
    n_list = [n // m for n in n_list]
    print_ln("n_list = %s", n_list)

# Call functions with the parsed parameters
check_inverse(d_list=d_list, epsilon=0.01)
model_inp_com(n, d_list, alpha, beta, m)
range_check(n)


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