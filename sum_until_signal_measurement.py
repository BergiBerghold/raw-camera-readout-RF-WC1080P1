from capture_frame import acquire_series_of_frames, return_camera_settings
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

max_intensity = 2
intensity_increment = 1
led_response_time = 5
number_of_summed_frames = 5000

# Create Directory for Data

try:
    measurement_name = sys.argv[1]
except:
    measurement_name = 'run'

timestamp = datetime.now().strftime('%H:%M:%S_%d.%m.')
measurement_directory = f'measurements/{measurement_name}_{timestamp}'
photo_directory = f'{measurement_directory}/photos'
os.makedirs(measurement_directory)
os.makedirs(photo_directory)

type_of_measurement = os.path.basename(__file__)[:-3]
open(f'{measurement_directory}/{type_of_measurement}', 'w').close()

# Calculate and print execution time

number_of_intensity_steps = (max_intensity + 1) / intensity_increment
number_of_measurement_points = number_of_intensity_steps * number_of_summed_frames
est_execution_time = number_of_intensity_steps * ( led_response_time + number_of_summed_frames * 0.26 )

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
measurement_metadata['type of measurement'] = type_of_measurement

df = pd.DataFrame.from_dict(measurement_metadata, orient='index', columns=['Value'])
df.to_csv(f'{measurement_directory}/measurement_metadata.csv', mode='w')

# Run measurement

start_time = time.time()
for intensity in range(0, max_intensity + 1, intensity_increment):
    set_led(intensity=intensity)
    photon_flux = calculate_flux(intensity)

    print(f'Measuring at intensity {intensity}...')
    time.sleep(led_response_time)

    y_channel_frames = acquire_series_of_frames(n_frames=number_of_summed_frames)
    print('Returned series of frames')

    y_channel_sum = np.zeros(y_channel_frames[0].shape, dtype=np.uint32)
    print('Initialized sum array')
    data_entry = []

    for idx, frame in enumerate(y_channel_frames):
        print(f'Summing frame no {idx}')
        y_channel_sum += frame

        center_square = y_channel_frames[515:566, 935:986]  # Returns the center 50x50 pixels
        data_entry.append(np.average(center_square) / (idx+1))

        if (idx+1) % 20 == 0:
            stretched_y_channel_sum = np.interp(y_channel_sum, (np.min(y_channel_sum), np.max(y_channel_sum)), (0, 255))

            img = Image.fromarray(stretched_y_channel_sum).convert('L')
            img.save(f'{photo_directory}/intens-{intensity}_frames-{idx+1}.png')

    df = pd.DataFrame([data_entry])
    df.to_csv(f'{measurement_directory}/datapoints.csv', mode='a', index=False, header=False)

set_led(intensity=0)

print(f'\n'
      f'Done.\n'
      f'Estimated execution time was {timedelta(seconds=est_execution_time)} ( hh:mm:ss )\n'
      f'Actual execution time was {timedelta(seconds=time.time()-start_time)} ( hh:mm:ss )')

