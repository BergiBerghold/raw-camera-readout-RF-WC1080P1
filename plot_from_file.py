import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

measurement_dir = '/Users/bergi/test_m/raw-webcam-readout/measurements/run_21:54:06_31.05.'

df = pd.read_csv(f'{measurement_dir}/datapoints.csv')
data_array = np.array(df)

df = pd.read_csv(f'{measurement_dir}/camera_settings.csv')
metadata = np.array(df)

data_array[:,0] *= 6.24150907 * 10**18

fig, ax = plt.subplots()

plt.plot(data_array[:,0], data_array[:,2], label='Average')
#plt.plot(data_array[:,0], data_array[:,3], label='Min')
plt.plot(data_array[:,0], data_array[:,4], label='Max')
plt.legend(loc="upper left")
plt.xlabel('Photons/s on entire sensor')

info_text = f'Measurement directory: {measurement_dir.split("/")[-1]}'
plt.annotate(info_text, xy = (0, -0.15), xycoords='axes fraction', horizontalalignment='left', verticalalignment='top')

metadata_left = '\n'.join([f'{x[0]}: {int(x[1])}' for x in metadata[:9]])
plt.annotate(metadata_left, xy = (0, -0.2), xycoords='axes fraction', horizontalalignment='left', verticalalignment='top')

metadata_right = '\n'.join([f'{x[0]}: {int(x[1])}' for x in metadata[9:]])
plt.annotate(metadata_right, xy = (0.5, -0.2), xycoords='axes fraction', horizontalalignment='left', verticalalignment='top')


fig.set_size_inches(9, 10)
fig.set_dpi(200)
fig.tight_layout()
plt.show()