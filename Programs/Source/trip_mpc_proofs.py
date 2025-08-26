import itertools
import math

from Compiler import types, library, instructions
from Compiler.types import sfix, sint, cfix, cint, Matrix, Array, personal
from Compiler import comparison, util
from Compiler import ml
from Programs.Source import random_matrix
from Compiler.library import start_timer, stop_timer, for_range_opt, print_ln, if_, break_loop, MemValue, for_range_opt_multithread
from Programs.Source.trip import generate_epsilon_matrix, generate_personal_array, generate_personal_matrix, share_personal_array, share_personal_matrix, mat_prod, count_greater_than_m, count_greater_than_m_secretly, count_smaller_than_m, count_smaller_than_m_secretly
fprecision = 16
types.sfix.set_precision(f=fprecision)
types.cfix.set_precision(f=fprecision)
n_threads = 48

def range_check_array(matrixy, B):
    result = (matrixy[:]< B )  
    result.reveal()
  

def range_check_matrix(matrixy, B):
    result = (matrixy[:][:] < B )  
    result.reveal()
  
def inverse_check(size, epsilon=0.0001):
    matrix_result = generate_epsilon_matrix(n=size, alpha=0, beta=0.00001)
    @for_range_opt_multithread(n_threads, size)
    def _(i):
        @for_range_opt_multithread(n_threads, size)
        def _(j):
            result = (matrix_result[i][j] < epsilon )  
            result.reveal()


def initial_input_commitment_proofs(n, d, alpha, beta, m, B):
    i=10  
    matrix_sxi = types.Matrix(1, d, sfix)
    matrix_sxit = types.Matrix(d, 1, sfix)
    start_timer(i)     
    # X_i rows are needed to check bounds.
    for j in range(m):
        matrix_si = generate_personal_matrix(j, 1, d, alpha, beta)
        matrix_sit = generate_personal_matrix(j, d, 1, alpha, beta)
        matrix_syr = generate_personal_array(j, n, alpha, beta)
    #@for_range_opt(m)
    #def _(k):
        @for_range_opt(n)
        def _(l):
            matrix_sxi = share_personal_matrix(matrix_si, 1, d)
            matrix_sxit = share_personal_matrix(matrix_sit, d, 1 ) 
        matrix_sy = share_personal_array(matrix_syr, n)    
        range_check_array(matrix_sy, B=B)
        range_check_array(matrix_sy, B=B)
    print_ln("finished with sharing")         
    @for_range_opt_multithread(n_threads, m)
    def _(k):
        BX =  mat_prod(matrix_sxi, matrix_sxit)    
    stop_timer(i)    
            
def model_input_commitment_proofs(n, d, alpha, beta, m):
    i=20
    # measure overhead of sharing personal matrix
    # has been computed in model_input_commitment of trip
    matrix_sa = types.Matrix(1, n, sfix)
    matrix_sb = types.Matrix(n, 1, sfix)
    matrix_sc = types.Matrix(1, d, sfix)
    matrix_sd = types.Matrix(d, 1, sfix)
    start_timer(i)
    for j in range(m):
        matrix_sar = generate_personal_matrix(j, 1, n, alpha, beta)
        matrix_sbr = generate_personal_matrix(j, n, 1, alpha, beta)
        matrix_scr = generate_personal_matrix(j, 1, d, alpha, beta)
        matrix_sdr = generate_personal_matrix(j, d, 1, alpha, beta)
    #@for_range_opt(m)
    #def _(k):
        matrix_sa = share_personal_matrix(matrix_sar, 1, n)
        matrix_sb = share_personal_matrix(matrix_sbr, n, 1)
        matrix_sc = share_personal_matrix(matrix_scr, 1, d)
        matrix_sd = share_personal_matrix(matrix_sdr, d, 1)
        
    @for_range_opt_multithread(n_threads, m)
    def _(k):    
        Ci = mat_prod(a=matrix_sa, b=matrix_sb)
        Ci = mat_prod(a=matrix_sa, b=matrix_sb)
        Ciii = mat_prod(a=matrix_sa, b=matrix_sb)
                
        D = mat_prod(a=matrix_sc, b=matrix_sd)    
        inverse_check(size=1)    
    stop_timer(i)        

def participation_set_update_proofs(n, m, alpha, beta):
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
        residuals_shared = share_personal_matrix(datasets[j], n, 1) 
    
    quantile = int (n*m / 2)
    
    q = dp_median_mpc(num_players=m, dataset_length=n, alpha=alpha, beta=beta, quantile=quantile, datasets=datasets, mal_flag=1)
        
    @for_range_opt(m)
    def _(k):
        # Generate a secure random dataset for each player
        @for_range_opt(n)
        def _(j):
            active_sets.append(residuals_shared[j] < q)
    #@for_range_opt(num_players)
    #def _(i):
    #    # Generate a secure random dataset for each player
    #    active_sets_shared[i].reveal_to(i)  
    stop_timer(i)       
    return active_sets



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
    
    # parties compute the result in mpc
    less_shared_malicious = types.Array(num_players,  types.sint)
    less_shared_malicious.assign_all(0)
    greater_shared_malicious = types.Array(num_players,  types.sint)
    greater_shared_malicious.assign_all(0)
    
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
            less = count_smaller_than_m(player=i, dataset=datasets[i], dataset_length=dataset_length, m=q)
            # count elements in the database of player i smaller than m
            greater = count_greater_than_m(player=i, dataset=datasets[i], dataset_length=dataset_length, m=q)
            
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
                greater_shared_malicious[i] = count_greater_than_m_secretly(dataset=datasets[i], dataset_length=dataset_length, m=m[k])
                less_shared_malicious[i] = count_smaller_than_m_secretly(dataset=datasets[i], dataset_length=dataset_length, m=m[k])
                cond = (less_shared_array[i] == less_shared_malicious[i]) 
                #library.runtime_error_if(cond.reveal() != 1, "Player  %s is malicious in initial" ,i)

        # Number of total elements
        n = dataset_length * num_players
        
        # MALICIOUS CHECK
        for i in range(num_players):  
            cond = (less_shared_array[i] + greater_shared_array[i]) <= dataset_length  
            library.runtime_error_if(cond.reveal() != 1, "Player  %s is malicious in malicious iterative" ,i)
            cond = (less_shared_array[i] >= less_to_verify[i]) 
            library.runtime_error_if(cond.reveal() != 1, "Player  %s is malicious in malicious iterative" ,i)
            cond = (greater_shared_array[i] >= greater_to_verify[i]) 
            library.runtime_error_if(cond.reveal() != 1, "Player  %s is malicious in  malicious iterative" ,i)
        
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

