import numpy as np
import matplotlib.pyplot as plt


csp_list = np.load('/Users/bergi/test_m/raw-webcam-readout/measurements/data_test.npy')

fig, ax = plt.subplots()

ax.plot(range(len(csp_list)), csp_list)

fig.set_size_inches(9, 10)
fig.set_dpi(200)
fig.tight_layout()
plt.show()