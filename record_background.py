from capture_frame import acquire_sum_of_frames, return_camera_settings
from datetime import datetime, timedelta
from led_driver import set_led
import pandas as pd
import numpy as np
import time
import sys
import os


# User Settings

brightness_setting = 200
number_of_summed_frames = 10000
led_response_time = 5

# Create Directory for Data

try:
    measurement_name = sys.argv[1]
except:
    measurement_name = 'background'

timestamp = datetime.now().strftime('%H:%M:%S_%d.%m.')
measurement_directory = f'measurements/{measurement_name}_{timestamp}'
os.makedirs(measurement_directory)

type_of_measurement = os.path.basename(__file__)[:-3]
open(f'{measurement_directory}/{type_of_measurement}', 'w').close()

# Calculate and print execution time

est_execution_time = number_of_summed_frames * 0.26

print(f'Taking and summing {number_of_summed_frames} frames.\n'
      f'Estimated execution time is {timedelta(seconds=est_execution_time)} ( hh:mm:ss )\n')

# Create CSV file containing the current camera and measurement settings

measurement_metadata = return_camera_settings()
measurement_metadata['led response time'] = led_response_time
measurement_metadata['number of summed frames'] = number_of_summed_frames
measurement_metadata['type of measurement'] = type_of_measurement

df = pd.DataFrame.from_dict(measurement_metadata, orient='index', columns=['Value'])
df.to_csv(f'{measurement_directory}/measurement_metadata.csv', mode='w')

# Define summation function


def sum_frames(sum_of_frames):
    global total_sum
    np.add(total_sum, sum_of_frames, out=total_sum)


# Run measurement

start_time = time.time()
set_led(intensity=0)
time.sleep(led_response_time)

frames_to_take = number_of_summed_frames
total_sum = np.zeros((1080, 1920), dtype=np.uint64)

while frames_to_take != 0:
    if frames_to_take >= 500:
        y_channel_frames, _, _ = acquire_sum_of_frames(n_frames=500, override_brightness=brightness_setting)
        sum_frames(y_channel_frames)
        del y_channel_frames
        frames_to_take -= 500

    elif frames_to_take > 0:
        y_channel_frames, _, _ = acquire_sum_of_frames(n_frames=frames_to_take, override_brightness=brightness_setting)
        sum_frames(y_channel_frames)
        del y_channel_frames
        frames_to_take = 0

with open(f'{measurement_directory}/summed_frame.raw', 'wb') as f:
    f.write(total_sum.tobytes())

print(f'\n'
      f'Done.\n'
      f'Estimated execution time was {timedelta(seconds=est_execution_time)} ( hh:mm:ss )\n'
      f'Actual execution time was {timedelta(seconds=time.time()-start_time)} ( hh:mm:ss )')
