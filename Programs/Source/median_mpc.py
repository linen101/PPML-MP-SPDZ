
#program.use_edabit(True)
import itertools
import random
import math
#import numpy as np
import sys
from Compiler import types, library, instructions
from Compiler.types import Array, cfix

from Compiler import comparison, util
from Programs.Source import random_matrix

fprecision = 16
types.sfix.set_precision(f=fprecision)
types.cfix.set_precision(f=fprecision)

m = 2            
n_list = [1000]
alpha =0
beta =1   

   
if len(sys.argv) > 2 and sys.argv[2].isdigit():  
    m = int(sys.argv[2])
    print_ln(" m  =  %s", m)
   

if len(sys.argv) > 3:  
    n_list = list(map(int, (sys.argv[3]).split(",")))
    n_list = [n // m for n in n_list]
    print_ln("n_list = %s", n_list)


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


def count_smaller_than_m(player, dataset, dataset_length, m):
    # element-wise comparison (A < m)
    comparison_results = types.personal(player, Array(dataset_length, types.cint))
    count = types.personal(player, cint(0))
    for i in range(dataset_length):
    #def _(i):
        c = (dataset[i] < m) + cint(0)
        count = count + c
        
        #print_ln(" value is: %s and m is: %s",sfix(dataset[i]).reveal(), sfix(m).reveal() )
        #print_ln(" comparison result is: %s",sint(c).reveal())
        #print_ln("true comparison result is: %s",sint(dataset[i] < m).reveal())
        
        #print_ln("count is:%s",sint(count).reveal())
        #print_ln("comparison has type%s",type(c))
        # Comparison operators (==, !=, <, <=, >, >=) are supported for cint, cfix, etc, returning regint()
        #comparison_results[i] = c 
        #ctypes.personal(player, cint(dataset[i] < m))
    #for i in range(dataset_length):
    #def _(i):
    #    count = comparison_results[i] + count
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
      
    # set possible k-th quantile value m for 1st round
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

def bench_naive_participation_set_update(num_players, dataset_length, alpha, beta):            
    # Matrix containing the residual errors of each party
    residuals_shared = types.Matrix(num_players, dataset_length, types.sfix)
    # Matrix containing the S vector of each party
    active_sets_shared = types.Matrix(num_players, dataset_length, types.sfix)
    i=1
    datasets = []
    #for n in n_list:
    # generate datasets 
    # for benchmark puproses only (not secure)
    start_timer(i)
    for j in range(num_players):
        # generate random datasets of range [alpha, beta]
        datasets.append(generate_personal_array(j, dataset_length, alpha, beta))
        residuals_shared = share_personal_matrix(datasets[j], dataset_length, 1) 
    stop_timer(i)
    
    quantile = int (dataset_length*num_players / 2)
    
    start_timer(i+1)
    q = median_mpc(num_players=num_players, dataset_length=dataset_length, alpha=alpha, beta=beta, quantile=quantile, datasets=datasets)
    stop_timer(i+1)
        
    start_timer(i+2)
    @for_range_opt(num_players)
    def _(i):
        # Generate a secure random dataset for each player
        @for_range_opt(dataset_length)
        def _(j):
            active_sets_shared[i][j] = (residuals_shared[i][j] < q)
    stop_timer(i+2)
        
        #i = i + 3
    return active_sets_shared
    
def bench_participation_set_update(n_list, m, alpha, beta):
    i=1
    #datasets = np.empty(m, dtype=object) 
    #active_sets = np.empty(m, dtype=object) 
    datasets = []
    active_sets = []
    # measure the time needed in MPC for Π_{qrankMPC}
    for n in n_list:
        # generate datasets 
        # for benchmark puproses only (not secure)
        start_timer(i)
        for j in range(m):
            # generate random datasets of range [alpha, beta]
            datasets.append(generate_personal_array(j, n, alpha, beta))
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
            active_sets.append(generate_personal_array(j, n, alpha, beta))
            share_personal_matrix(active_sets[j], n, 1) 
        stop_timer(i+2)    
        
        i = i + 3


def bench_median_mpc(n_list, m, alpha, beta):
    i=1
    #datasets = np.empty(m, dtype=object) 
    datasets = []
    # measure the time needed in MPC for Π_{qrankMPC}
    for n in n_list:
        # generate  datasets 
        # for benchmark puproses only (not secure)
        for j in range(m):
            # generate random datasets of range [alpha, beta]
            #datasets[j] = generate_personal_array(j, n, alpha, beta)
            personal_array = generate_personal_array(j, n, alpha, beta)
            datasets.append(personal_array)
            
        quantile = int (n*m / 2)
        
        start_timer(i)
        q = median_mpc(num_players=m, dataset_length=n, alpha=alpha, beta=beta, quantile=quantile, datasets=datasets)
        stop_timer(i)  
        
        i = i + 1

       
#bench_participation_set_update(n_list, m, alpha, beta)        
#bench_median_mpc(n_list, m, alpha, beta)
bench_naive_participation_set_update(num_players=2, dataset_length=10, alpha=0, beta=1)