import numpy as np
# import matplotlib as plt
import matplotlib.pyplot as plt

# Constants
D0 = 1.34e-5  # m^2/s
Ea = 48311  # J/mol
R = 8.314  # J/(mol*K)
initial_moisture_content = 0.08  # wt.%
depths = [0, 0.22, 2 * 0.22, 3 * 0.22, 4 * 0.22, 5 * 0.22]  # mm
depths_m = [d / 1000 for d in depths]  # convert to meters

# Environmental conditions
conditions = [
 {"T": 25 + 273.15, "RH": 95, "days": 2},
 {"T": 110 + 273.15, "RH": 5, "days": 6 / 60 / 24},
 {"T": 110 + 273.15, "RH": 5, "days": 7 / 60 / 24},
 {"T": 25 + 273.15, "RH": 95, "days": 2},
 {"T": 110 + 273.15, "RH": 5, "days": 8 / 60 / 24}
]


# Functions
def calculate_diffusivity(T):
 return D0 * np.exp(-Ea / (R * T))


def calculate_equilibrium_moisture(RH):
 return 0.1813 * (RH / 100) + 0.0229  # CETIM data


# Time arrays
time_arrays = [np.linspace(0, cond["days"] * 24 * 3600, 10000) for cond in conditions]

# Moisture content calculations
moisture_content_arrays = [[] for _ in range(len(conditions))]

for depth in depths_m:
 moisture_content = initial_moisture_content
 for i, cond in enumerate(conditions):
  D = calculate_diffusivity(cond["T"])
  Em = calculate_equilibrium_moisture(cond["RH"])
  time = time_arrays[i]
  sidedness_factor = 0.5
  moisture_content_cond = moisture_content + (Em - moisture_content) * sidedness_factor * (
           1 - np.exp(-7.3 * (D * time / (depth ** 2)) ** 0.75))
  moisture_content_arrays[i].append(moisture_content_cond)
  moisture_content = moisture_content_cond[-1]

# Plotting
fig, axs = plt.subplots(5, 1, figsize=(12, 20))

for i, cond in enumerate(conditions):
 for j, depth in enumerate(depths):
  if i in [1, 2, 4]:
   axs[i].plot(time_arrays[i] / 60, moisture_content_arrays[i][j], label=f'Depth = {depth} mm')
  else:
   axs[i].plot(time_arrays[i] / 3600, moisture_content_arrays[i][j], label=f'Depth = {depth} mm')
 axs[i].set_ylabel('Moisture Content (wt.%)')
 axs[i].set_xlabel('Time (min)' if i in [1, 2, 4] else 'Time (h)')
 axs[i].set_title(f"Condition {i + 1}: T = {cond['T'] - 273.15}°C, RH = {cond['RH']}%")
 axs[i].grid(True, which='both', linestyle='--', linewidth=0.5)
 axs[i].minorticks_on()
 if i == 0:
  axs[i].legend()

plt.tight_layout()
plt.show()


