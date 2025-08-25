#import numpy as np
import itertools
import random
import math
import sys

from Compiler import types, library, instructions
from Compiler import comparison, util
from Compiler import ml
from Programs.Source import random_matrix
from Programs.Source.trip_mpc_proofs import *

# Default values (optional)
m = 2  # Number of parties
n = 5  # Number of samples
d = 1  # Number of features

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

# Call functions with the parsed parameters
alpha = 0
beta = 1 
B = 10
#initial_input_commitment_proofs(n, d, alpha, beta, m, B) 
#model_input_commitment_proofs(n, d, alpha, beta , m)
participation_set_update_proofs(n, m, alpha, beta)

