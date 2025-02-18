import matplotlib.pyplot as plt
import numpy as np

# Data for scaling with n, d=100, N=2
n_values = [1000, 10000, 100000]
x_labels = ["n=1000", "n=10000", "n=100000"]
initial_input_commitment = [2.903, 28.670, 278.697]
model_input_commitment = [4.729, 30.004, 282.288]
model_update = [250.896, 250.896, 250.896]  # Assuming constant
model_reveal = [0.120, 0.120, 0.120]  # Assuming constant
participation_set_update  = [48.96,  51.54, 63.83 ]
total_scaling = np.array(initial_input_commitment) + np.array(model_input_commitment) + np.array(model_update) + np.array(model_reveal)
x_positions = np.arange(len(x_labels))

# Plot scaling for each phase with n (linear scale)
plt.figure(figsize=(8, 6))
plt.plot(x_positions, initial_input_commitment, marker='o', color="tomato", label="Initial Input Commitment")
plt.plot(x_positions, model_input_commitment, marker='s', color="chocolate", label="Model Input Commitment")
plt.plot(x_positions, model_update, marker='^', linestyle="dashed", color="indianred", label="Model Update")
plt.plot(x_positions, model_reveal, marker='d', linestyle="dashed", color="darkorange", label="Model Reveal")
plt.plot(x_positions, participation_set_update, marker='x', color="peru", label="Participation Set Update")


plt.xticks(x_positions, x_labels)
plt.xlabel("Number of Samples")
plt.ylabel("Time (sec)")
plt.title("Scaling of Each Phase with n (d=100, N=2)")
plt.legend()
plt.grid(False)
plt.show()

# Plot total scaling with n (linear scale)
plt.figure(figsize=(8, 6))
plt.plot(x_positions, total_scaling, marker='o', color="darksalmon", label="Total Computation Time")
plt.xticks(x_positions, x_labels)
plt.xlabel("Number of Samples")
plt.ylabel("Time (sec)")
plt.title("Total Scaling with n (d=100, N=2)")
plt.legend()
plt.grid(False)
plt.show()

# Data for scaling with d, n=100K, N=2
d_values_100k = [25, 50, 75, 100, 150, 200, 300]
initial_input_commitment_100k = [74.232, 143.901, 213.955, 278.697, 416.187, 557.637, 847.058]
model_input_commitment_100k = [70.869, 140.531, 210.381, 282.288, 426.771, 567.524, 860.741]
model_update_100k = [54.879, 88.021, 169.470, 250.896, 491.023, 754.193, 1511.920]
model_reveal_100k = [0.121, 0.120, 0.120, 0.120, 0.120, 0.120, 0.120]
participation_set_update_100k  =  [63.83, 63.83,63.83, 63.83, 63.83,63.83, 63.83 ]

total_scaling_d_100k = np.array(initial_input_commitment_100k) + np.array(model_input_commitment_100k) + np.array(model_update_100k) + np.array(model_reveal_100k) +  np.array(participation_set_update_100k)

# Plot scaling for each phase with d (linear scale)
plt.figure(figsize=(8, 6))
plt.plot(d_values_100k, initial_input_commitment_100k, marker='o', color="tomato", label="Initial Input Commitment")
plt.plot(d_values_100k, model_input_commitment_100k, marker='s', color="chocolate", label="Model Input Commitment")
plt.plot(d_values_100k, model_update_100k, marker='^', color="indianred", label="Model Update")
plt.plot(d_values_100k, model_reveal_100k, marker='d', linestyle="dashed", color="darkorange", label="Model Reveal")
plt.plot(d_values_100k, participation_set_update_100k, marker='x',linestyle="dashed", color="peru", label="Participation Set Update")

plt.xlabel("Number of Features (d)")
plt.ylabel("Time (sec)")
plt.title("Scaling of Each Phase with d (n=100K, N=2)")
plt.legend()
plt.grid(False)
plt.show()

# Plot total scaling with d for n=100K (linear scale)
plt.figure(figsize=(8, 6))
plt.plot(d_values_100k, total_scaling_d_100k, marker='o', color="darksalmon", label="Total Computation Time")
plt.xlabel("Number of Features (d)")
plt.ylabel("Time (sec)")
plt.title("Total Scaling with d (n=100K, N=2)")
plt.legend()
plt.grid(False)
plt.show()
