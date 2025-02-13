import random
from Compiler import types, library

def generate_matrix(num_rows, num_columns, lower_bound=0, upper_bound=100):
    """
    Generate a matrix with the given dimensions filled with sfix values 
    from a uniform distribution between lower_bound and upper_bound.
    
    :param num_rows: Number of rows in the matrix.
    :param num_columns: Number of columns in the matrix.
    :param lower_bound: Lower bound for the uniform distribution.
    :param upper_bound: Upper bound for the uniform distribution.
    :return: Matrix of sfix values.
    """
    matrix = types.Matrix(num_rows, num_columns,  types.sfix)
    for i in range(num_rows):
        for j in range(num_columns):
            value = random.uniform(lower_bound, upper_bound)
            matrix[i][j] =  types.sfix(value)
    return matrix

def generate_keys(length, lower_bound=0, upper_bound=100):
    """
    Generate an array of keys for the radix sort with sfix values 
    from a uniform distribution between lower_bound and upper_bound.
    
    :param length: Number of keys.
    :param lower_bound: Lower bound for the uniform distribution.
    :param upper_bound: Upper bound for the uniform distribution.
    :return: Array of sfix values.
    """
    keys = types.Array(length, types.sfix)
    for i in range(length):
        value = random.uniform(lower_bound, upper_bound)
        keys[i] = types.sfix(value)
    return keys

def generate_array(length, a, b):
    # Set global precision for sfix
    m = types.Array(length,  types.sfix)
    for i in range(length):
        value = random.uniform(a, b)
        m[i] =  types.sfix(value)
    return m
