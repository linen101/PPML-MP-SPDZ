import numpy as np
import matplotlib.pyplot as plt

# Given data
n = np.array([10, 100, 1000])
times = np.array([3.93117, 53.699, 635.652])

# Plot the original data
plt.figure(figsize=(10, 6))
plt.scatter(n, times, color='blue', label='Original Data')

# Estimate and plot for larger inputs (extrapolation based on observed trend)
n_large = np.array([10000, 100000])

# Assuming a rough estimation based on the existing trend
# We'll use log-log scale to observe the pattern
log_n = np.log(n)
log_times = np.log(times)
coefficients = np.polyfit(log_n, log_times, 1)
slope, intercept = coefficients

# Extrapolate
log_n_large = np.log(n_large)
log_times_large = slope * log_n_large + intercept
times_large = np.exp(log_times_large)

plt.scatter(n_large, times_large, color='red', label='Estimated Data')

# Plot the trend line
n_all = np.concatenate((n, n_large))
log_n_all = np.log(n_all)
log_times_all = slope * log_n_all + intercept
times_all = np.exp(log_times_all)

plt.plot(n_all, times_all, label='Trend Line', linestyle='--')

# Customize plot
plt.xscale('log')
plt.yscale('log')
plt.xlabel('Input Size (n)')
plt.ylabel('Computation Time')
plt.title('Computation Time vs Input Size')
plt.legend()
plt.grid(True)
plt.show()
