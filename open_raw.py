import matplotlib.colors as colr
import matplotlib.pyplot as plt
import numpy as np


file = 'summed_frame.raw'

raw_data = np.fromfile(file, dtype=np.uint64)
frame = raw_data.reshape(1080, 1920)

frame_norm = np.zeros((1080, 1920), dtype=np.float64)
frame_norm = frame / 10000

print(frame_norm[500, 500])

plt.imshow(frame_norm, cmap='gray')#, norm=colr.Normalize(vmin=89828, vmax=200000, clip=False))
plt.xlabel(f'min.: {np.min(frame_norm)}/max.: {np.max(frame_norm)}')
plt.show()

# plt.hist(frame.flatten(), bins=10000)
# plt.semilogy()
# plt.show()
