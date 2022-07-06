from capture_frame import acquire_series_of_frames, return_camera_settings
from datetime import datetime, timedelta
from led_driver import set_led
from random import randint
from PIL import Image
import pandas as pd
import numpy as np
import time
import sys
import os


# User Settings

intensity = 1000
whitebalance_temp = 4600    # min=2800 max=6500 step=1 default=4600
measurements = 200
led_response_time = 5
frames_to_take = 20
gain = 255
brightness = 255


# Calculate and print execution time

camera_fps = 4
est_execution_time = measurements * frames_to_take / camera_fps

print(f'Doing {measurements} measurements with {frames_to_take} frames each.\n'
      f'Estimated execution time is {timedelta(seconds=est_execution_time)} ( hh:mm:ss )\n')

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
photo_directory = f'{measurement_directory}/photos'
os.makedirs(measurement_directory)
os.makedirs(photo_directory)

type_of_measurement = os.path.basename(__file__)[:-3]
open(f'{measurement_directory}/{type_of_measurement}', 'w').close()


# Create CSV file for data points

header = [f'Frame {x+1}' for x in range(frames_to_take)]
df = pd.DataFrame(columns=header)
df.to_csv(f'{measurement_directory}/datapoints.csv', mode='w', index=False, header=True)


# Create CSV file containing the current camera and measurement settings

measurement_metadata = return_camera_settings()
measurement_metadata['override brightness'] = brightness
measurement_metadata['override gain'] = gain
measurement_metadata['override wbt'] = whitebalance_temp
measurement_metadata['frames to take'] = frames_to_take
measurement_metadata['intensity'] = intensity
measurement_metadata['measurements'] = measurements
measurement_metadata['led response time'] = led_response_time
measurement_metadata['type of measurement'] = type_of_measurement

df = pd.DataFrame.from_dict(measurement_metadata, orient='index', columns=['Value'])
df.to_csv(f'{measurement_directory}/measurement_metadata.csv', mode='w')


# Run measurement

set_led(intensity=intensity)
time.sleep(led_response_time)
start_time = time.perf_counter()

for point in range(measurements):
    print(f'    Measuring datapoint {point+1} of {measurements}...')

    frames = acquire_series_of_frames(frames_to_take, override_gain=gain,
                                      override_brightness=brightness, override_wbt=whitebalance_temp)

    csp_array = []

    for frame in frames:
        frame_bincount = np.bincount(frame.flatten())
        count_of_second_peak = sorted(frame_bincount)[-2]
        csp_array.append(count_of_second_peak)

    data_entry = csp_array
    df = pd.DataFrame([data_entry])
    df.to_csv(f'{measurement_directory}/datapoints.csv', mode='a', index=False, header=False)

set_led(intensity=0)

print(f'Done with measurement.\n'
      f'Estimated execution time was {timedelta(seconds=est_execution_time)} ( hh:mm:ss )\n'
      f'Actual execution time was {timedelta(seconds=time.perf_counter() - start_time)} ( hh:mm:ss )\n\n\n')