import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv('/Users/bergi/test_m/raw-webcam-readout/measurements/run_21:54:06_31.05./datapoints.csv')
data_array = np.array(df)

data_array[:,0] *= 6.24150907 * 10**18

plt.plot(data_array[:,0], data_array[:,2], label='Average')
#plt.plot(data_array[:,0], data_array[:,3], label='Min')
plt.plot(data_array[:,0], data_array[:,4], label='Max')
plt.legend(loc="upper left")
plt.xlabel('Photons/s on entire sensor')
plt.figtext(0.5,0.5, "Text under the Plot", ha="center", va="center", fontsize=18)
plt.show()