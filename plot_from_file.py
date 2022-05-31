import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv('/Users/bergi/test_m/raw-webcam-readout/measurements/run_16:55:06_31.05./data.csv')
data_array = np.array(df)

plt.plot(data_array[:,0], data_array[:,2])
plt.show()