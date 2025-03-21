#program.use_edabit(True)
#import matplotlib.pyplot as plt
import numpy as np

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

### test generate sorted array of random uniform numbers for a player ###
# this is not secure: array_random is given in the clear to everyone
# and all of the players perform the sorting
# it is not possible to create a sorting with control-flow for personal values in the high- level
def generate_sorted_personal_array(player, length, alpha, beta):
    array_a = types.personal(player, Array(length, types.cfix))
    array_random = np.random.uniform(alpha, beta, length)
    array_random_sorted = sorted(array_random)
    for i in range(length):
        value = array_random_sorted[i]
        #print_ln("init value: %s" , value)
        value_cfix =  types.cfix(value)
        #print_ln("cfix value: %s" , value_cfix)
        array_a[i] = value_cfix
    return array_a

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

def count_smaller_than_m(player, dataset, dataset_length, m):
    # element-wise comparison (A < m)
    comparison_results = types.personal(player, Array(dataset_length, types.cint))
    count = types.personal(player, cint(0))
    for i in range(dataset_length):
    #def _(i):
        c = (dataset[i] < m) + cint(0)
        count = count + c
    # Sum the binary results to count
    return count

def count_smaller_than_m_secretly( dataset, dataset_length, m):
    # element-wise comparison (A < m)
    comparison_results = types.Array(dataset_length, types.sint)
    count = types.sint(0)
    for i in range(dataset_length):
    #def _(i):
        c = (sint(dataset[i]) < m) + sint(0)
        count = count + c
    return count    

def count_greater_than_m(player, dataset, dataset_length, m):
    # element-wise comparison (A < m)
    comparison_results = types.personal(player, Array(dataset_length, types.cint))
    count = types.personal(player, cint(0))
    for i in range(dataset_length):
    #def _(i):
        c = (dataset[i] > m) + cint(0)
        count = count + c
    return count    

def count_greater_than_m_secretly( dataset, dataset_length, m):
    # element-wise comparison (A < m)
    comparison_results = types.Array(dataset_length, types.sint)
    count = types.sint(0)
    for i in range(dataset_length):
    #def _(i):
        c = (sint(dataset[i]) > m) + sint(0)
        count = count + c
    return count    

### implement median mpc from 
# Secure Computation of the kth-Ranked Element
# for fixed point numbers.
def median_mpc(num_players, dataset_length, alpha, beta, quantile, datasets):  
    # datasets will store all the personal datasets in one place
        
    # suggested lower range
    a = types.Array(fprecision+1,  types.cfix)
    # suggested upper range
    b = types.Array(fprecision+1,  types.cfix)
    # suggested median
    m = types.Array(fprecision+1,  types.cfix)
    
    # malicious
    less_to_verify = types.Array(num_players,  types.sint)
    less_to_verify.assign_all(0)
    greater_to_verify = types.Array(num_players,  types.sint)
    greater_to_verify.assign_all(0)
    
    # party i shares the result
    less_shared_array = types.Array(num_players,  types.sint)
    greater_shared_array = types.Array(num_players,  types.sint)
    
    # parties compute the result in mpc
    less_shared_malicious = types.Array(num_players,  types.sint)
    less_shared_malicious.assign_all(0)
    greater_shared_malicious = types.Array(num_players,  types.sint)
    greater_shared_malicious.assign_all(0)
      
    
    # set possible k-th quantile value m for this round
    a[0] = cfix(alpha)
    b[0] = cfix(beta)
    
    # Initialize return value
    q = cfix(0)
    @for_range_opt(2*fprecision)
    def _(k):
        # Compute median candidate
        m[k] = cfix((a[k] + b[k]) / 2)
        q.update(m[k])
        print_ln("Iteration %s: a = %s, b = %s, m = %s", k, a[k], b[k], m[k])
        sum_less_shared = sint(0)
        sum_greater_shared = sint(0)
        
        for i in range(num_players):
            # count elements in the database of player i smaller than m
            less = count_smaller_than_m(player=i, dataset=datasets[i], dataset_length=dataset_length, m=m[k])
            # count elements in the database of player i smaller than m
            greater = count_greater_than_m(player=i, dataset=datasets[i], dataset_length=dataset_length, m=m[k])
            
            # secret share the personal less than result of player i.
            less_shared = sint(less)
            print_ln("Smaller than values of player %s : %s",i, less_shared.reveal()) 
            
            # secret share the personal greater than result of player i.
            greater_shared = sint(greater)
            print_ln("Greater than values of player %s: %s", i, greater_shared.reveal())
            
            # update the arrays to keep the secret-shared results.
            less_shared_array[i] = less_shared
            greater_shared_array[i] = greater_shared 

            # compute sums
            sum_less_shared = less_shared + sum_less_shared
            sum_greater_shared = greater_shared + sum_greater_shared
           
            # verify input in the protocol
            #@if_(k==0)
            #def _():
            #    start_timer(2)
            #    greater_shared_malicious[i] = count_greater_than_m_secretly(dataset=datasets[i], dataset_length=dataset_length, m=m[k])
            #    less_shared_malicious[i] = count_smaller_than_m_secretly(dataset=datasets[i], dataset_length=dataset_length, m=m[k])
            #    cond = (less_shared_array[i] == less_shared_malicious[i]) 
            #    library.runtime_error_if(cond.reveal() != 1, "Player  %s is malicious" ,i)
            #    stop_timer(2)

        # Number of total elements
        n = dataset_length * num_players
        
        # Print sums
        #print_ln("Sum of Smaller than values: %s", sum_less_shared.reveal()) 
        #print_ln("Sum of Greater than values: %s", sum_greater_shared.reveal())
        
        # MALICIOUS CHECK
        for i in range(num_players):  
            cond = (less_shared_array[i] + greater_shared_array[i]) <= dataset_length  
            library.runtime_error_if(cond.reveal() != 1, "Player  %s is malicious" ,i)
            cond = (less_shared_array[i] >= less_to_verify[i]) 
            library.runtime_error_if(cond.reveal() != 1, "Player  %s is malicious" ,i)
            cond = (greater_shared_array[i] >= greater_to_verify[i]) 
            library.runtime_error_if(cond.reveal() != 1, "Player  %s is malicious" ,i)
        
        # Update a and b based on the sums
        #cond = (sum_less_shared >= quantile)
        #print_ln("Condition is  %s for sum %s and quantile %s", cond.reveal(), sum_less_shared.reveal(), quantile)
       
        
        @if_((sum_less_shared >= quantile).reveal())
        def _():
            b[k + 1] = m[k] - 2**(-fprecision)    # narrow upper bound
            a[k + 1] = a[k]
            #print_ln("Updating b[%s] to %s", k + 1, b[k + 1])
            for i in range(num_players):
                greater_to_verify[i] = dataset_length - less_shared_array[i]
        @if_((sum_greater_shared >= n - quantile + 1).reveal())
        def _():
            a[k + 1] = m[k] + 2**(-fprecision)   # narrow lower bound
            b[k + 1] = b[k]
            #print_ln("Updating a[%s] to %s", k + 1, a[k + 1])
            for i in range(num_players):
                less_to_verify[i] = dataset_length - greater_shared_array[i]        

        # Termination condition (median found)
        @if_((sum_less_shared < quantile).reveal() & (sum_greater_shared <= n - quantile).reveal())
        def _():
            print_ln("Median found: %s", m[k])
            q.update(m[k])
            break_loop()
    return q        
"""        
#1/2 - quantile
dataset_length = 100
num_players = 2
quantile = int (dataset_length*num_players / 2)
#print_ln("k-th rank to be found is: %s", quantile)
q = median_mpc(num_players=num_players, dataset_length=dataset_length, alpha=0, beta=1, quantile= quantile)      
#print_ln("%s Quantile value is: %s", quantile, q)  
"""   

def active_set_update(num_players, dataset_length, alpha, beta, q):
    # Matrix containing the residual errors of each party
    residuals_shared = types.Matrix(num_players, dataset_length, types.sfix)
    # Matrix containing the S vector of each party
    active_sets_shared = types.Matrix(num_players, dataset_length, types.sfix)
    for i in range(num_players):
        # Generate a secure random dataset for each player
        personal_array = generate_personal_array(i, dataset_length, alpha, beta)
        @for_range_opt(dataset_length)
        def _(j):
            residuals_shared[i][j] = personal_array[j]
    start_timer(3)
    @for_range_opt(num_players)
    def _(i):
        # Generate a secure random dataset for each player
        @for_range_opt(dataset_length)
        def _(j):
            active_sets_shared[i][j] = (residuals_shared[i][j] < q)
    stop_timer(3)
    #@for_range_opt(num_players)
    #def _(i):
    #    # Generate a secure random dataset for each player
    #    active_sets_shared[i].reveal_to(i)         
    return active_sets_shared
    
#active_set_update(num_players=2, dataset_length=100000, alpha=0, beta=1, q=0.37)

def bench_participation_set_update(n_list, m, alpha, beta):
    i=40
    datasets = np.empty(m, dtype=object) 
    active_sets = np.empty(m, dtype=object) 
    # measure the time needed in MPC for Π_{qrankMPC}
    for n in n_list:
        # generate sorted datasets 
        # for benchmark puproses only (not secure)
        start_timer(i)
        for j in range(m):
            # generate random datasets of range [alpha, beta]
            datasets[j] = generate_sorted_personal_array(j, n, alpha, beta)
            share_personal_matrix(datasets[j], n, 1) 
            # print values for testing
            #for j in range(dataset_length):
                #print_ln("value %s of player %s is %s", j, i, sfix(datasets[i][j]).reveal()) 
        stop_timer(i)
        
        quantile = int (n*m / 2)
        
        start_timer(i+1)
        q = median_mpc(num_players=m, dataset_length=n, alpha=alpha, beta=beta, quantile=quantile, datasets=datasets)
        stop_timer(i+1)
        
        start_timer(i+2)
        for j in range(m):
            # generate random datasets of range [alpha, beta]
            active_sets[j] = generate_personal_array(j, n, alpha, beta)
            share_personal_matrix(active_sets[j], n, 1) 
        stop_timer(i+2)    
        
        i = i + 3



def mat_prod(a, b):
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
"""
# input size           
dataset_length = 100000
features = 10

# A: [dxd], B: [dx1]
matrix_a = generate_random_shared_matrix(features, features, alpha =0,   beta=1)
matrix_b = generate_random_shared_matrix(features, 1, alpha=0, beta=1)
"""
def initial_input_commitment(n, d_list, alpha, beta, m):
    i=1
    for d in d_list: 
        start_timer(i)
        for p in range(m):  
            matrix_x = generate_personal_matrix(p, n, d, alpha,   beta)
            matrix_y = generate_personal_matrix(p, n, 1, alpha,   beta)

            # measure overhead of sharing personal matrix
            matrix_sx = share_personal_matrix(matrix_x, n, d)
            matrix_sy = share_personal_matrix(matrix_y, n, 1)
        stop_timer(i)
        i = i + 1

def model_input_commitment(n, d_list, alpha, beta, m):
    i=10
    for d in d_list: 
        start_timer(i) 
        for p in range(m):        
            # D: [dxn], C:[dxd] ,  A: [dxd], B: [dx1], H: [dxd]
            matrix_d = generate_personal_matrix(p, d, n, alpha, beta)        
            matrix_c = generate_personal_matrix(p, d, d, alpha, beta)
            matrix_a = generate_personal_matrix(p, d, d, alpha, beta)
            matrix_b = generate_personal_matrix(p, d, 1, alpha, beta)
            matrix_h = generate_personal_matrix(p, d, d, alpha=0, beta=  2**(-fprecision))

            # measure overhead of sharing personal matrix
            matrix_sd = share_personal_matrix(matrix_d, d, n)
            
            matrix_sc = share_personal_matrix(matrix_c, d, d)
            
            matrix_sa = share_personal_matrix(matrix_a, d, d)  
            
            matrix_sb = share_personal_matrix(matrix_b, d, 1)  
            
            matrix_sh = share_personal_matrix(matrix_h, d, d)  
        stop_timer(i)
        i = i + 1
        


def model_update(n, d_list, alpha, beta, m):
    i=20
    for d in d_list:
        # measure overhead of sharing personal matrix
        # has been computed in model_input_commitment
        matrix_sa = generate_random_shared_matrix(d, d, alpha, beta)
        matrix_sb = generate_random_shared_matrix(d, 1, alpha, beta)
        matrix_swu = generate_random_shared_matrix(d, 1, alpha, beta)

        # measure overhead of matrix mult in ADMM
        start_timer(i)
        @for_range_opt(m)
        def _(j):
            @for_range_opt(10)
            def _(k):
                # measure overhead of d mult -> ADMM
                C = mat_prod(a=matrix_sa, b=matrix_sb)    
            
                D = mat_prod(a=matrix_sa, b=matrix_swu)    
                
        stop_timer(i)        
        i = i + 1

def model_reveal(n, d_list, alpha, beta):   
    # measure time for opening w
    i = 30
    for d in d_list:
        matrix_sw = generate_random_shared_matrix(d, 1, alpha, beta)
        start_timer(i)
        matrix_sw.reveal()
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

initial_input_commitment(n, d_list, alpha, beta, m) 
model_input_commitment(n, d_list, alpha, beta , m)
model_update(n, d_list, alpha, beta, m)
model_reveal(n, d_list, alpha, beta)
bench_participation_set_update(n_list, m, alpha, beta)

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