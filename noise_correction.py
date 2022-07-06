from capture_frame import acquire_sum_of_frames, return_camera_settings
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from led_driver import set_led
import pandas as pd
import numpy as np
import time
import sys
import os

n_frames = 10
y_channel, _, _ = acquire_sum_of_frames(n_frames=n_frames)

noise = np.fromfile('noise_normalized.raw', dtype=np.float64).reshape(1080, 1920)
noise *= n_frames

y_channel_subtracted = y_channel.astype(np.float64) - noise

fig, ax = plt.subplots()

plt.subplot(3, 1, 1)
plt.imshow(y_channel, cmap='nipy_spectral')  # , norm=colr.Normalize(vmin=20000, vmax=25000, clip=False))
plt.title('Original Image')
plt.xlabel(f'min.: {np.min(y_channel)}/max.: {np.max(y_channel)}')

plt.subplot(3, 1, 2)
plt.imshow(noise, cmap='nipy_spectral')  # , norm=colr.Normalize(vmin=20000, vmax=25000, clip=False))
plt.title('Noise')
plt.xlabel(f'min.: {np.min(noise)}/max.: {np.max(noise)}')

plt.subplot(3, 1, 3)
plt.imshow(y_channel_subtracted, cmap='nipy_spectral')  # , norm=colr.Normalize(vmin=20000, vmax=25000, clip=False))
plt.title('Noise Subtracted Image')
plt.xlabel(f'min.: {np.min(y_channel_subtracted)}/max.: {np.max(y_channel_subtracted)}')

fig.set_size_inches(12, 16)
plt.show()