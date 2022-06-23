import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colr


raw_file = 'summed_frame.raw'

raw_data = np.fromfile(raw_file, dtype=np.uint64)
array_frame = raw_data.reshape(1080, 1920)

plt.imshow(array_frame, cmap='gray', norm=colr.Normalize(vmin=9035, vmax=20000, clip=True))
plt.xlabel(f'min.: {np.min(array_frame)}/max.: {np.max(array_frame)}')
plt.show()

# plt.hist(array_frame.flatten(), bins=1000)
# plt.semilogy()
# plt.show()