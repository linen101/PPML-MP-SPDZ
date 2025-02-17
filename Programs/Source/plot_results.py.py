import matplotlib.pyplot as plt
import numpy as np

# Data from table for n = 100k and parties = 2
d_values = [25, 50, 75, 100, 150, 200, 300]

initial_input_commitment = [74.232, 143.901, 213.955, 278.697, 416.187, 557.637, 847.058]
model_input_commitment = [70.869, 140.531, 210.381, 282.288, 426.771, 567.524, 860.741]
model_update = [54.879, 88.021, 169.470, 250.896, 491.023, 754.193, 1511.920]
model_reveal = [0.121, 0.120, 0.120, 0.120, 0.120, 0.120, 0.120]
participation_set_update = [None, None, None, 63.838, None, None, None]

# Plotting
plt.figure(figsize=(10, 6))

plt.plot(d_values, initial_input_commitment, marker='o', label='Initial Input Commitment')
plt.plot(d_values, model_input_commitment, marker='s', label='Model Input Commitment')
plt.plot(d_values, model_update, marker='^', label='Model Update')
plt.plot(d_values, model_reveal, marker='d', label='Model Reveal')

# Handling None values for participation_set_update (only valid for d=100)
valid_d = [d_values[3]]  # d=100 where data exists
valid_participation = [participation_set_update[3]]
plt.scatter(valid_d, valid_participation, color='red', label='Participation Set Update', zorder=3)

plt.xlabel('Number of Features (d)')
plt.ylabel('Time (ms)')
plt.title('Scaling of Phases with d for n=100k (Parties=2)')
plt.legend()
plt.grid(True)

# Show plot
plt.show()