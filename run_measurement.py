from photon_calculator import calculate_flux
from capture_frame import do_capture
from led_driver import set_led
from datetime import datetime
from PIL import Image
import pandas as pd
import numpy as np
import os
import time


frames = 100

now = datetime.now()
timestamp = now.strftime('%H:%M:%S_%d.%m.')

if not os.path.exists('measurements'):
    os.mkdir('measurements')

run_directory = f'measurements/run_{timestamp}'
os.mkdir(run_directory)

df = pd.DataFrame([['Photon Flux', 'Intensity', 'Average', 'Min.', 'Max.']])
df.to_csv(f'{run_directory}/data.csv', mode='w', index=False, header=False)

for intensity in range(0, 65536, 1000):
    set_led(intensity=intensity)
    photon_flux = calculate_flux(intensity)

    time.sleep(4)

    sum_of_y_channel, _, _ = do_capture(n_frames=frames)
    norm_sum_of_y_channel = sum_of_y_channel / frames

    data_entry = [photon_flux,
                  intensity,
                  np.average(norm_sum_of_y_channel),
                  np.min(norm_sum_of_y_channel),
                  np.max(norm_sum_of_y_channel)]

    stretched_sum_of_y_channel = np.interp(sum_of_y_channel, (np.min(sum_of_y_channel), np.max(sum_of_y_channel)), (0, 255))
    Image.fromarray(stretched_sum_of_y_channel).convert('L').save(f'{run_directory}/{intensity}_sum_y.png')

    df = pd.DataFrame([data_entry])
    df.to_csv(f'{run_directory}/data.csv', mode='a', index=False, header=False)
    print(data_entry)

set_led(intensity=0)