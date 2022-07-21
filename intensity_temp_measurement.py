from capture_frame import acquire_series_of_frames, return_camera_settings
from photon_calculator import calculate_flux
from evaluate_signal import evaluate_signal
from datetime import datetime, timedelta
from led_driver import set_led
from PIL import Image
import pandas as pd
import numpy as np
import time
import sys
import os


# User Settings


intensity = 300
averaged_frames = 30
throwaway_frames = 10
min_temp = 15
max_temp = 50
temp_increment = 5


# Calculate and print execution time

camera_fps = 4
time_to_thermal_equil = 60
number_of_temp_steps = len(range(min_temp, max_temp, temp_increment))
est_execution_time = number_of_temp_steps * ( time_to_thermal_equil + 1/camera_fps * (averaged_frames+throwaway_frames))

print(f'Measuring from {min_temp} °C to {max_temp} °C in steps of {temp_increment} °C at intensity {intensity}, '
      f'resulting in {number_of_temp_steps} data points.\n'
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
os.makedirs(measurement_directory)

type_of_measurement = os.path.basename(__file__)[:-3]
open(f'{measurement_directory}/{type_of_measurement}', 'w').close()


# Create CSV file for data points

header = ['Photon Flux', 'LED Intensity', 'Temperature', 'Second Peak Count', 'Histogram Metric']
df = pd.DataFrame(columns=header)
df.to_csv(f'{measurement_directory}/datapoints.csv', mode='w', index=False, header=True)


# Create CSV file containing the current camera and measurement settings

measurement_metadata = return_camera_settings()
measurement_metadata['averaged frames'] = averaged_frames
measurement_metadata['throwaway frames'] = throwaway_frames
measurement_metadata['minimum temperature'] = min_temp
measurement_metadata['maximum temperature'] = max_temp
measurement_metadata['temperature increment'] = temp_increment
measurement_metadata['type of measurement'] = type_of_measurement

df = pd.DataFrame.from_dict(measurement_metadata, orient='index', columns=['Value'])
df.to_csv(f'{measurement_directory}/measurement_metadata.csv', mode='w')


# Run measurement

start_time = time.time()
set_led(intensity=intensity)
photon_flux = calculate_flux(intensity)

for temp in range(min_temp, max_temp, temp_increment):
    input(f'Set Temperature to {temp} °C. Press Enter when done')

    print('Waiting for temperature to be reached...\n')

    while True:
        with open('temp_log.txt', 'r') as f:
            line = eval(f.readlines()[-1])
            actual_temp = float(line['probe'])
            print(f'Sensor has {actual_temp}/{temp} °C    ', end='\r')

        if abs(actual_temp - temp) <= 0.25:
            print('\nTemperature reached!\n')
            break

    frames = acquire_series_of_frames(averaged_frames + throwaway_frames)[throwaway_frames:]
    sum_of_frames = np.zeros(frames[0].shape, dtype=np.uint64)
    avrg_count_of_second_peak = 0

    for frame in frames:
        frame_bincount = np.bincount(frame.flatten())
        count_of_second_peak = sorted(frame_bincount)[-2]
        avrg_count_of_second_peak += count_of_second_peak

        np.add(sum_of_frames, frame, out=sum_of_frames)

    avrg_count_of_second_peak /= averaged_frames
    hist_metric = evaluate_signal(sum_of_frames)

    data_entry = [photon_flux, intensity, temp, avrg_count_of_second_peak, hist_metric]
    df = pd.DataFrame([data_entry])
    df.to_csv(f'{measurement_directory}/datapoints.csv', mode='a', index=False, header=False)

set_led(intensity=0)

print(f'Done with measurement.\n'
      f'Estimated execution time was {timedelta(seconds=est_execution_time)} ( hh:mm:ss )\n'
      f'Actual execution time was {timedelta(seconds=time.time()-start_time)} ( hh:mm:ss )\n\n\n')
