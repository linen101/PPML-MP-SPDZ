import itertools
import math

from Compiler import types, library, instructions
from Compiler.types import sfix, sint, cfix, cint, Matrix, Array, personal
from Compiler import comparison, util
from Compiler import ml
from Programs.Source import random_matrix
from Compiler.library import start_timer, stop_timer, for_range_opt, print_ln, if_, break_loop, MemValue, for_range_opt_multithread
from Programs.Source.trip import generate_epsilon_matrix, generate_personal_array, generate_personal_matrix, share_personal_array, share_personal_matrix, median_mpc, dp_median_mpc, mat_prod
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
    
    q = median_mpc(num_players=m, dataset_length=n, alpha=alpha, beta=beta, quantile=quantile, datasets=datasets, mal_flag=1)
        
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

