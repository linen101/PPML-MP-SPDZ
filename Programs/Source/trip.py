#program.use_edabit(True)
#import matplotlib.pyplot as plt
#import numpy as np
import itertools
#import random
import math

from Compiler import types, library, instructions
from Compiler.types import sfix, sint, cfix, cint, Matrix, Array, personal
from Compiler import comparison, util
from Compiler import ml
from Programs.Source import random_matrix
from Compiler.library import start_timer, stop_timer, for_range_opt, print_ln, if_, break_loop, MemValue
fprecision = 16
types.sfix.set_precision(f=fprecision)
types.cfix.set_precision(f=fprecision)

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

def generate_personal_array(player, length, alpha, beta):
    # Set global precision for sfix...
    array_a = types.personal(player, Array(length, types.cfix))
    @for_range_opt(length)
    def _(i):
        #value = random.uniform(alpha, beta)
        value = cint(42)/cint(i)
        value_cfix =  types.cfix(value)
        array_a[i] = value_cfix
    return array_a 

def generate_personal_matrix(player, n, d, alpha, beta):
    matrix_a = types.personal(player, types.Matrix(n, d, types.cfix))
    @for_range_opt(n)
    def _(i):
        @for_range_opt(d)
        def _(j):
            # not secure for benchmark puproses only
            #value = random.uniform(alpha, beta)
            value = cint(42)/cint(i)
            value_cfix =  types.cfix(value)
            matrix_a[i][j] = value_cfix
    return matrix_a  

def share_personal_array(array_a, n):
    array_sa = sfix.Array(n)
    array_sa[:] = sfix(array_a[:])
    return array_sa  

def share_personal_matrix(matrix_a, n, d):
    matrix_sa = sfix.Matrix(n, d)
    matrix_sa[:] = sfix(matrix_a[:])
    return matrix_sa  

def generate_random_shared_matrix(n, d, alpha, beta):
    # Set global precision for sfix...
    matrix_a = types.Matrix(n, d, types.sfix)
    @for_range_opt(n)
    def _(i):
        @for_range_opt(d)
        def _(j):
            #value = random.uniform(alpha, beta)
            value = cint(42)/cint(i)
            value_sfix =  types.sfix(value)
            matrix_a[i][j] = value_sfix
    return matrix_a  

def generate_random_shared_array(n, alpha, beta):
    # Set global precision for sfix...
    matrix_a = types.Array(n, types.sfix)
    @for_range_opt(n)
    def _(i):
        #value = random.uniform(alpha, beta)
        value = cint(42)/cint(i)
        value_sfix =  types.sfix(value)
        matrix_a[i] = value_sfix
    return matrix_a

###   Generate a diagonal matrix with random uniform values for a player ###
def generate_epsilon_matrix(n, alpha, beta):
    matrix_a = types.Matrix(n, n, types.cfix)
    matrix_a.assign_all(0)
    @for_range_opt(n)
    def _(i):
        matrix_a[i][i] = cfix(1)
    return matrix_a

def count_smaller_than_m(player, dataset, dataset_length, m):
    # element-wise comparison (A < m)
    comparison_results = types.personal(player, Array(dataset_length, types.cint))
    count = types.personal(player, cint(0))
    #MemValue(count)
    c = types.personal(player, Array(dataset_length, types.cint))
    b = types.Array(dataset_length, types.cint)
    b.assign_all(1)
    c[:] = b[:]
    comparison_results = dataset[:] < m
    for i in range(dataset_length):
        #def _(i):
        #c = (dataset[i] < m) + cint(0)
        count + comparison_results[i]
    # Sum the binary results to count
    #return count

def count_greater_than_m(player, dataset, dataset_length, m):
    # element-wise comparison (A < m)
    comparison_results = types.personal(player, Array(dataset_length, types.cint))
    count = types.personal(player, cint(0))
    for i in range(dataset_length):
    #def _(i):
        c = (dataset[i] > m) + cint(0)
        count = count + c
    return count    

### for malicious consistency checks in MPC
def count_smaller_than_m_secretly( dataset, dataset_length, m):
    # element-wise comparison (A < m)
    comparison_results = types.Array(dataset_length, types.sint)
    count = types.sint(0)
    for i in range(dataset_length):
    #def _(i):
        c = (sint(dataset[i]) < m) + sint(0)
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

### implement median mpc from:
# Secure Computation of the kth-Ranked Element
# for fixed point numbers.
def median_mpc(num_players, dataset_length, alpha, beta, quantile, datasets, mal_flag=0):  
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
            #print_ln("Smaller than values of player %s : %s",i, less_shared.reveal()) 
            
            # secret share the personal greater than result of player i.
            greater_shared = sint(greater)
            #print_ln("Greater than values of player %s: %s", i, greater_shared.reveal())
            
            # update the arrays to keep the secret-shared results.
            less_shared_array[i] = less_shared
            greater_shared_array[i] = greater_shared 

            # compute sums
            sum_less_shared = less_shared + sum_less_shared
            sum_greater_shared = greater_shared + sum_greater_shared
           
            # verify input in the protocol
            @if_(k==0 & mal_flag==1)
            def _():
                greater_shared_malicious[i] = count_greater_than_m_secretly(dataset=datasets[i], dataset_length=dataset_length, m=m[k])
                less_shared_malicious[i] = count_smaller_than_m_secretly(dataset=datasets[i], dataset_length=dataset_length, m=m[k])
                cond = (less_shared_array[i] == less_shared_malicious[i]) 
                library.runtime_error_if(cond.reveal() != 1, "Player  %s is malicious" ,i)

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
            #print_ln("Median found: %s", m[k])
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
def dp_median_mpc(num_players, dataset_length, alpha, beta, quantile, datasets, mal_flag=0): 
    e = cfix(math.e)
    step = 2**(-fprecision)    
    # suggested lower range
    a = types.Array(2*fprecision+1,  types.cfix)
    # suggested upper range
    b = types.Array(2*fprecision+1,  types.cfix)
    # suggested median
    m = types.Array(2*fprecision+1,  types.cfix)
    
    # malicious
    less_to_verify = types.Array(num_players,  types.sint)
    less_to_verify.assign_all(0)
    greater_to_verify = types.Array(num_players,  types.sint)
    greater_to_verify.assign_all(0)
    
    # party i shares the result
    less_shared_array = types.Array(num_players,  types.sint)
    greater_shared_array = types.Array(num_players,  types.sint)
      
    # set possible k-th quantile value m for 1st round
    a[0] = cfix(alpha)
    b[0] = cfix(beta)
    
    # Initialize return value
    q = cfix(0)
    @for_range_opt(2*fprecision)
    def _(k):
        #c=sint()
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
            #print_ln("Smaller than values of player %s : %s",i, less_shared.reveal()) 
            
            # secret share the personal greater than result of player i.
            greater_shared = sint(greater)
            #print_ln("Greater than values of player %s: %s", i, greater_shared.reveal())
            
            # update the arrays to keep the secret-shared results.
            less_shared_array[i] = less_shared
            greater_shared_array[i] = greater_shared 

            # compute sums
            sum_less_shared = less_shared + sum_less_shared
            sum_greater_shared = greater_shared + sum_greater_shared

            # verify input in the protocol
            @if_(k==0 & mal_flag)
            def _():
                # parties compute the result in mpc
                less_shared_malicious = types.Array(num_players,  types.sint)
                less_shared_malicious.assign_all(0)
                greater_shared_malicious = types.Array(num_players,  types.sint)
                greater_shared_malicious.assign_all(0)
      
                greater_shared_malicious[i] = count_greater_than_m_secretly(dataset=datasets[i], dataset_length=dataset_length, m=m[k])
                less_shared_malicious[i] = count_smaller_than_m_secretly(dataset=datasets[i], dataset_length=dataset_length, m=m[k])
                cond = (less_shared_array[i] == less_shared_malicious[i]) 
                library.runtime_error_if(cond.reveal() != 1, "Player  %s is malicious" ,i)

        # Number of total elements
        n = dataset_length * num_players
        
        # MALICIOUS CHECK
        for i in range(num_players):  
            cond = (less_shared_array[i] + greater_shared_array[i]) <= dataset_length  
            library.runtime_error_if(cond.reveal() != 1, "Player  %s is malicious" ,i)
            cond = (less_shared_array[i] >= less_to_verify[i]) 
            library.runtime_error_if(cond.reveal() != 1, "Player  %s is malicious" ,i)
            cond = (greater_shared_array[i] >= greater_to_verify[i]) 
            library.runtime_error_if(cond.reveal() != 1, "Player  %s is malicious" ,i)
        
        # Print sums
        #print_ln("Sum of Smaller than values: %s", sum_less_shared.reveal())         
        w_a = sfix(1)
        w_b = sfix(1)
        
        #compute weights
        x = sum_less_shared - quantile
        #print_ln('utility is: %s', x.reveal())
        x_abs = abs(x)
        x_exp = sfix(-x_abs)
        c1 =  x_abs - 12
        cond1 = c1 < 0
        e_x = cond1.if_else(e**x_exp, 0)
        #print_ln('exp(%s)=%s',x_exp.reveal() ,e_x.reveal())
        
        c = x < 0
        w_a = c.if_else(e_x, 1)
        w_b = c.if_else(1, e_x)
                
    
        # Update a and b based on the weights
        w_total = w_a + w_b
        t = sfix.get_random(0,1)
        #print_ln("t is : %s",t.reveal())
        w_total_random = w_total*t
        cond = w_a < w_total_random
        cond = cond.reveal()
        @if_(cond==1)
        def _():
            a[k+1] = m[k] + step
            b[k+1] = b[k]
            for i in range(num_players):
                less_to_verify[i] = dataset_length - greater_shared_array[i]          
        @if_(cond==0)
        def _():
            a[k+1] = a[k]
            b[k+1] = m[k] -step  
            for i in range(num_players):
                greater_to_verify[i] = dataset_length - less_shared_array[i]
        # Termination condition (median found)
        @if_( (b[k+1]==a[k+1]) )
        def _():
            print_ln("Median found: %s",a[k+1])
            q.update(a[k+1])
            break_loop()        
    return q

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


def initial_input_commitment(n, d, alpha, beta, m):
    i=1
    start_timer(i)
    for p in range(m):  
        matrix_x = generate_personal_matrix(p, n, d, alpha,   beta)
        matrix_y = generate_personal_matrix(p, n, 1, alpha,   beta)

        # measure overhead of sharing personal matrix
        matrix_sx = share_personal_matrix(matrix_x, n, d)
        matrix_sy = share_personal_matrix(matrix_y, n, 1)
    stop_timer(i)

def model_input_commitment(n, d, alpha, beta, m):
    i=10
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
        
def model_update(n, d, alpha, beta, m):
    i=20
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

def model_reveal(n, d, alpha, beta):   
    # measure time for opening w
    i = 30
    matrix_sw = generate_random_shared_matrix(d, 1, alpha, beta)
    start_timer(i)
    matrix_sw.reveal()
    stop_timer(i)

def participation_set_update(n, m, alpha, beta):
    i=40
    datasets = []
    active_sets = []
    # measure the time needed in MPC for Π_{qrankMPC}
    # generate sorted datasets 
    # for benchmark puproses only (not secure)
    start_timer(i)
    for j in range(m):
        # generate random datasets of range [alpha, beta]
        datasets.append(generate_personal_array(j, n, alpha, beta))
        share_personal_matrix(datasets[j], n, 1) 
        # print values for testing
        #for j in range(dataset_length):
            #print_ln("value %s of player %s is %s", j, i, sfix(datasets[i][j]).reveal()) 
    #stop_timer(i)
    
    quantile = int (n*m / 2)
    
    #start_timer(i+1)
    q = dp_median_mpc(num_players=m, dataset_length=n, alpha=alpha, beta=beta, quantile=quantile, datasets=datasets)
    #stop_timer(i+1)
    
    #start_timer(i+2)
    for j in range(m):
        # generate random datasets of range [alpha, beta]
        active_sets.append(generate_personal_array(j, n, alpha, beta))
        share_personal_matrix(active_sets[j], n, 1) 
    stop_timer(i)
    #stop_timer(i+2)    

#participation_set_update(100, 2, 1, 2)