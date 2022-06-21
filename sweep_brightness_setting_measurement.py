from capture_frame import acquire_sum_of_frames, return_camera_settings
from photon_calculator import calculate_flux
from datetime import datetime, timedelta
from led_driver import set_led
import pandas as pd
import numpy as np
import time
import sys
import os

# User Settings

brightness_setting_sweep_increment = 2      # [Camera Brightness Units]
intensity_increment = 100                   # [DAC steps]
max_intensity = 30000                       # [DAC steps]
led_response_time = 5                       # [seconds]

# Calculate and print execution time

number_of_intensity_steps = len(range(0, max_intensity + 1, intensity_increment))
est_execution_time = number_of_intensity_steps * ( led_response_time + 3 * 0.3 * 255 / brightness_setting_sweep_increment )

print(f'Measuring from 0 to {max_intensity} intensity in steps of {intensity_increment}, '
      f'resulting in {number_of_intensity_steps} data points.\n'
      f'Estimated maximum execution time is {timedelta(seconds=est_execution_time)} ( hh:mm:ss )\n')

while True:
    user_input = input('Continue? (y/n)')

    if user_input == 'y':
        print('Starting...\n')
        break
    elif user_input == 'n':
        exit()

# Create Directory for Data

try:
    measurement_name = sys.argv[1]
except:
    measurement_name = 'run'

timestamp = datetime.now().strftime('%H:%M:%S_%d.%m.')
measurement_directory = f'measurements/{measurement_name}_{timestamp}'
os.makedirs(measurement_directory)

type_of_measurement = os.path.basename(__file__)[:-3]
open(f'{measurement_directory}/{type_of_measurement}', 'w').close()

# Create CSV file for data points

header = ['Photon Flux', 'LED Intensity', 'Brightness Setting required']
df = pd.DataFrame(columns=header)
df.to_csv(f'{measurement_directory}/datapoints.csv', mode='w', index=False, header=True)
print(header)

# Create CSV file containing the current camera and measurement settings

measurement_metadata = return_camera_settings()
measurement_metadata['brightness_setting_sweep_increment'] = brightness_setting_sweep_increment
measurement_metadata['maximum intensity'] = max_intensity
measurement_metadata['intensity increment'] = intensity_increment
measurement_metadata['led response time'] = led_response_time
measurement_metadata['type of measurement'] = type_of_measurement

df = pd.DataFrame.from_dict(measurement_metadata, orient='index', columns=['Value'])
df.to_csv(f'{measurement_directory}/measurement_metadata.csv', mode='w')


# Define Test function

def test_frame(frame):
    # 1920 * 1080 / 1000 = 2074

    return np.count_nonzero( np.bincount(frame.flatten()) > 2074 ) >= 2

# Run measurement

start_time = time.time()
for intensity in range(0, max_intensity + 1, intensity_increment):
    set_led(intensity=intensity)
    photon_flux = calculate_flux(intensity)

    print(f'Measuring at intensity {intensity}...')
    time.sleep(led_response_time)

    required_brightness = 255

    for brightness in range(0, 256, brightness_setting_sweep_increment):
        sum_of_y_channel, _, _ = acquire_sum_of_frames(n_frames=1, override_brightness=brightness)

        if test_frame(sum_of_y_channel):
            confirmation_1, _, _ = acquire_sum_of_frames(n_frames=1, override_brightness=brightness)
            confirmation_2, _, _ = acquire_sum_of_frames(n_frames=1, override_brightness=brightness)
            confirmation_3, _, _ = acquire_sum_of_frames(n_frames=1, override_brightness=brightness)

            if test_frame(confirmation_1) and test_frame(confirmation_2) and test_frame(confirmation_3):
                print(f'    Got signal at camera brightness setting of {brightness}')
                required_brightness = brightness

                break

    data_entry = [photon_flux, intensity, required_brightness]
    df = pd.DataFrame([data_entry])
    df.to_csv(f'{measurement_directory}/datapoints.csv', mode='a', index=False, header=False)

set_led(intensity=0)

print(f'\n'
      f'Done.\n'
      f'Estimated execution time was {timedelta(seconds=est_execution_time)} ( hh:mm:ss )\n'
      f'Actual execution time was {timedelta(seconds=time.time()-start_time)} ( hh:mm:ss )')