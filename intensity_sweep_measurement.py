from capture_frame import acquire_frames, return_camera_settings
from photon_calculator import calculate_flux
from datetime import datetime, timedelta
from led_driver import set_led
from PIL import Image
import pandas as pd
import numpy as np
import time
import sys
import os

# User Settings

frames = 100                    # [Frames per measurement point]
intensity_increment = 1000      # [DAC steps]
led_response_time = 4           # [seconds]

# Create Directory for Data

try:
    measurement_name = sys.argv[1]
except:
    measurement_name = 'run'

timestamp = datetime.now().strftime('%H:%M:%S_%d.%m.')
measurement_directory = f'measurements/{measurement_name}_{timestamp}'
os.makedirs(measurement_directory)

# Calculate and print execution time

led_dac_resolution = 65536
number_of_measurement_points = led_dac_resolution / intensity_increment
est_execution_time = number_of_measurement_points * (led_response_time + frames * 0.2)

print(f'Starting measurement every {intensity_increment} DAC steps with {frames} frames each, '
      f'resulting in {int(led_dac_resolution / intensity_increment)} data points.\n'
      f'Estimated execution time is {timedelta(seconds=est_execution_time)} ( hh:mm:ss )\n')

# Create CSV file for data points

header = ['Photon Flux', 'Intensity', 'Average', 'Min.', 'Max.']
df = pd.DataFrame(columns=header)
df.to_csv(f'{measurement_directory}/datapoints.csv', mode='w', index=False, header=True)
print(header)

# Create CSV file containing the current camera settings

df = pd.DataFrame.from_dict(return_camera_settings(), orient='index', columns=['Value'])
df.to_csv(f'{measurement_directory}/camera_settings.csv', mode='w')

# Run measurement for each intensity

for intensity in range(0, 65536, intensity_increment):
    set_led(intensity=intensity)
    photon_flux = calculate_flux(intensity)

    time.sleep(led_response_time)

    sum_of_y_channel, _, _ = acquire_frames(n_frames=frames)
    norm_sum_of_y_channel = sum_of_y_channel / frames

    data_entry = [photon_flux,
                  intensity,
                  np.average(norm_sum_of_y_channel),
                  np.min(norm_sum_of_y_channel),
                  np.max(norm_sum_of_y_channel)]

    stretched_sum_of_y_channel = np.interp(sum_of_y_channel, (np.min(sum_of_y_channel), np.max(sum_of_y_channel)), (0, 255))
    Image.fromarray(stretched_sum_of_y_channel).convert('L').save(f'{measurement_directory}/{intensity}_sum_y.png')

    df = pd.DataFrame([data_entry])
    df.to_csv(f'{measurement_directory}/datapoints.csv', mode='a', index=False, header=False)
    print(data_entry)

set_led(intensity=0)
