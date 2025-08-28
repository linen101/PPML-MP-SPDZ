#import numpy as np
import itertools
import random
import math

from Compiler import types, library, instructions
from Compiler import comparison, util
from Compiler import ml
from Programs.Source import random_matrix

from Programs.Source.trip import *
import sys

from Sampling.primitives_mpc import distributed_sample, bitwise_sample


n=1
m=2
start_timer(2)
print_ln("parties:%s", m)
print_ln("samples:%s", n)
test = sint(1)
print_ln("test: %s", test.reveal())
noised_y = bitwise_sample(n=n, s=1, mechanism='gauss', binary=0, num_party=m) # use bitwise sampling
stop_timer(2)