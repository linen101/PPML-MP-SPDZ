import itertools
import math

from Compiler import types, library, instructions
from Compiler.types import sfix, sint, cfix, cint, Matrix, Array, personal
from Compiler import comparison, util
from Compiler import ml
from Programs.Source import random_matrix
from Compiler.library import start_timer, stop_timer, for_range_opt, print_ln, if_, break_loop, MemValue
from Programs.Source.trip import *
fprecision = 16
types.sfix.set_precision(f=fprecision)
types.cfix.set_precision(f=fprecision)

def range_check_array(size, B):
    matrix_result = generate_random_shared_array(size, alpha=0, beta=1)
    @for_range_opt(size)
    def _(i):
        result = (matrix_result[i]< B )  
        result.reveal()
  

def range_check_matrix(size, B):
    matrix_result = generate_random_shared_matrix(size, alpha=0, beta=1)
    @for_range_opt(size)
    def _(i):
        @for_range_opt(size)
        def _(i):
            result = (matrix_result[i][j] < q )  
            result.reveal()
  
def inverse_check(size, epsilon=0.0001):
    matrix_result = generate_epsilon_matrix(n=size, alpha=0, beta=0.00001)
    @for_range_opt(size)
    def _(i):
        @for_range_opt(size)
        def _(j):
            result = (matrix_result[i][j] < epsilon )  
            result.reveal()

def initial_input_commitment_proofs(n, d, alpha, beta, m, B):
    i=10  
    # X_i rows are needed to check bounds.
    matrix_sxi = generate_random_shared_matrix(1, d, alpha, beta)
    matrix_sxit = generate_random_shared_matrix(d, 1, alpha, beta)
    matrix_sy = generate_random_shared_matrix(n, 1, alpha, beta)  
    @for_range_opt(m)
    def _(j): 
        @for_range_opt(n)
        def _(i):
            BX =  mat_prod(a=matrix_sxi, b=matrix_sxit)
            range_check_array(size=n, B=B)
        range_check_array(size=n, B=B)
            
def model_input_commitment_proofs(n, d, alpha, beta, m):
    i=20
    # measure overhead of sharing personal matrix
    # has been computed in model_input_commitment of trip
    matrix_sa = generate_random_shared_matrix(1, n, alpha, beta)
    matrix_sb = generate_random_shared_matrix(n, 1, alpha, beta)
    matrix_sc = generate_random_shared_matrix(1, d, alpha, beta)
    matrix_sd = generate_random_shared_matrix(d, 1, alpha, beta)
    start_timer(i)
    @for_range_opt(m)
    def _(j):
        @for_range_opt(3)
        def _(i):
            C = mat_prod(a=matrix_sa, b=matrix_sb)
                
        D = mat_prod(a=matrix_sc, b=matrix_sd)    
        inverse_check(size=d)    
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
    def _(i):
        # Generate a secure random dataset for each player
        @for_range_opt(n)
        def _(j):
            active_sets.append(residuals_shared[j] < q)
    #@for_range_opt(num_players)
    #def _(i):
    #    # Generate a secure random dataset for each player
    #    active_sets_shared[i].reveal_to(i)         
    return active_sets

