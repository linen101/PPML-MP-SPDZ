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

start_timer(1)
noised_y = bitwise_sample(n=1, s=0.5, mechanism='gauss', binary=0, num_party=2) # use bitwise sampling
stop_timer(1)