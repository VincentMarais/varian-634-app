import numpy as np
import matplotlib.pyplot as plt

# Constants
a_mean = -32.02
a_std = 0.26
b_mean = 886.13
b_std = 2.70

# Generating sample data
x = np.linspace(0, 10, 100)
y_mean = a_mean * x + b_mean

# Calculating standard deviation of y based on given formula
# Since std(y) = std(a*x + b) = sqrt((x^2)*(std(a)^2) + (std(b)^2))
# But, as there's a little confusion in the interpretation, assuming it's a general line plotting with shaded std error area
y_std = np.sqrt((x**2) * a_std**2 + b_std**2)

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(x, y_mean, label='Mean Regression Line')
plt.fill_between(x, y_mean - y_std, y_mean + y_std, color='gray', alpha=0.2, label='Standard Deviation')
plt.title('Mean Regression Line with Standard Deviation')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.grid(True)
plt.show()