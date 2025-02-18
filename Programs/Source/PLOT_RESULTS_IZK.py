import matplotlib.pyplot as plt
import numpy as np

# Values for when the number of parties (P) = 2 and n = 100k
d_values_100k = [25, 50, 75, 100, 150, 200, 300]

# Data extracted from the table for n = 100k, P = 2
initial_input_commitment_100k = [4.918, 5.038, 5.650, 6.116, 6.928, 9.362, 13.402]
model_input_commitment_100k = [635.832, 1287.034, 1990.482, None, None, None, 7581.8]  # X means no data provided
participation_set_update_100k = [10.8, 10.8, 10.8, 10.8, 10.8, 10.8, 10.8]

# Convert None values to NaN for correct plotting
model_input_commitment_100k = np.array([x if x is not None else np.nan for x in model_input_commitment_100k])

# Compute total scaling (sum of available phases)
total_scaling_100k = np.array(initial_input_commitment_100k) + model_input_commitment_100k + np.array(participation_set_update_100k)

# Plot Scaling for Each Phase (Dashed Lines)
plt.figure(figsize=(8, 6))
plt.plot(d_values_100k, initial_input_commitment_100k, marker='o', linestyle="dashed", color="tomato", label="Initial Input Commitment")
plt.plot(d_values_100k, model_input_commitment_100k, marker='s', linestyle="dashed", color="chocolate", label="Model Input Commitment")
plt.plot(d_values_100k, participation_set_update_100k, marker='^', linestyle="dashed", color="peru", label="Participation Set Update")

plt.xlabel("Number of Features (d)")
plt.ylabel("Time (sec)")
plt.title("Scaling of Each Phase with d (n=100k, P=2)")
plt.legend()
plt.grid(False)
plt.show()

# Plot Total Scaling (Dashed Lines)
plt.figure(figsize=(8, 6))
plt.plot(d_values_100k, total_scaling_100k, marker='o', linestyle="dashed", color="darksalmon", label="Total Computation Time")

plt.xlabel("Number of Features (d)")
plt.ylabel("Time (sec)")
plt.title("Total Scaling with d (n=100k, P=2)")
plt.legend()
plt.grid(False)
plt.show()

# Values for when the number of parties (P) = 2 and d = 100
n_values_100d = [1000, 10000, 100000]

# Data extracted from the table for n = 100k, P = 2
initial_input_commitment_100d = [4.406, 4.550, 6.116]
model_input_commitment_100d = [16.529, 1158.91, None]  # X means no data provided
participation_set_update_100d = [7.98, 8.96, 10.8]

# Convert None values to NaN for correct plotting
model_input_commitment_100d = np.array([x if x is not None else np.nan for x in model_input_commitment_100d])

# Compute total scaling (sum of available phases)
total_scaling_100d = np.array(initial_input_commitment_100d) + model_input_commitment_100d + np.array(participation_set_update_100d)

######################### n scaling ###########################
x_labels = ["n=1000", "n=10000", "n=100000"]
x_positions = np.arange(len(x_labels))

# Plot Scaling for Each Phase (Dashed Lines)
plt.figure(figsize=(8, 6))
plt.plot(x_positions, initial_input_commitment_100d, marker='o', linestyle="dashed", color="darkturquoise", label="Initial Input Commitment")
plt.plot(x_positions, model_input_commitment_100d, marker='s', linestyle="dashed", color="darkcyan", label="Model Input Commitment")
plt.plot(x_positions, participation_set_update_100d, marker='^', linestyle="dashed", color="lightseagreen", label="Participation Set Update")

plt.xticks(x_positions, x_labels)
plt.xlabel("Number of Samples (n)")
plt.ylabel("Time (sec)")
plt.title("Scaling of Each Phase with n (d=100, P=2)")
plt.legend()
plt.grid(False)
plt.show()

# Plot Total Scaling (Dashed Lines)
plt.figure(figsize=(8, 6))
plt.plot(n_values_100d, total_scaling_100d, marker='o', linestyle="dashed", color="cadetblue", label="Total Computation Time")

plt.xlabel("Number of Samples (n)")
plt.ylabel("Time (sec)")
plt.title("Total Scaling with n (d=100, P=2)")
plt.legend()
plt.grid(False)
plt.show()
