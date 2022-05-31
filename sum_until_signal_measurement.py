import numpy as np

from capture_frame import acquire_series_of_frames, return_camera_settings
from photon_calculator import calculate_flux
from datetime import datetime, timedelta
from led_driver import set_led
import pandas as pd
import time
import sys
import os


# User Settings

max_intensity = 100
intensity_increment = 1
led_response_time = 4
number_of_summed_frames = 1000

# Create Directory for Data

try:
    measurement_name = sys.argv[1]
except:
    measurement_name = 'run'

timestamp = datetime.now().strftime('%H:%M:%S_%d.%m.')
measurement_directory = f'measurements/{measurement_name}_{timestamp}'
os.makedirs(measurement_directory)

# Calculate and print execution time

number_of_measurement_points = max_intensity / intensity_increment * number_of_summed_frames
est_execution_time = max_intensity / intensity_increment * ( led_response_time + number_of_summed_frames * 0.2 )

print(f'Measuring from 0 to {max_intensity} intensity in steps of {intensity_increment} and '
      f'up to {number_of_summed_frames} frames, resulting in {number_of_measurement_points} data points.\n'
      f'Estimated execution time is {timedelta(seconds=est_execution_time)} ( hh:mm:ss )\n')

# Create CSV file for data points

header = [f'{x} Frames' for x in range(1, number_of_summed_frames)]
df = pd.DataFrame(columns=header)
df.to_csv(f'{measurement_directory}/datapoints.csv', mode='w', index=False, header=True)

# Create CSV file containing the current camera and measurement settings

measurement_metadata = return_camera_settings()
measurement_metadata['maximum intensity'] = max_intensity
measurement_metadata['intensity increment'] = intensity_increment
measurement_metadata['led response time'] = led_response_time
measurement_metadata['number of summed frames'] = number_of_summed_frames
measurement_metadata['type of measurement'] = os.path.basename(__file__)[:-3]

df = pd.DataFrame.from_dict(measurement_metadata, orient='index', columns=['Value'])
df.to_csv(f'{measurement_directory}/measurement_metadata.csv', mode='w')

# Run measurement

for intensity in range(0, max_intensity, intensity_increment):
    set_led(intensity=intensity)
    photon_flux = calculate_flux(intensity)

    time.sleep(led_response_time)

    y_channel_frames = acquire_series_of_frames(n_frames=number_of_summed_frames)

    y_channel_sum = np.zeros(y_channel_frames[0].shape)
    data_entry = []

    for frame, idx in enumerate(y_channel_frames):
        y_channel_sum += frame
        data_entry.append(np.average(y_channel_sum) / (idx+1))

    df = pd.DataFrame([data_entry])
    df.to_csv(f'{measurement_directory}/datapoints.csv', mode='a', index=False, header=False)

set_led(intensity=0)

