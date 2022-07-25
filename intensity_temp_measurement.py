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


min_intensity = 0
max_intensity = 400
intensity_increment = 10
averaged_frames = 40
throwaway_frames = 10
min_temp = -15
max_temp = 60
temp_increment = 5


# Calculate and print execution time

camera_fps = 4
led_response_time = 5
time_to_thermal_equil = 90
number_of_steps = len(range(min_intensity, max_intensity, intensity_increment)) * len(range(min_temp, max_temp, temp_increment))
est_execution_time = number_of_steps * (1/camera_fps * (averaged_frames+throwaway_frames) + led_response_time) + len(range(min_temp, max_temp, temp_increment)) * time_to_thermal_equil

print(f'Measuring {number_of_steps} data points.\n'
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

header = ['Target Temperature', 'Mean Temperature', 'Minimum Temperature', 'Maximum Temperature', 'LED Intensity', 'Second Peak Count', 'Histogram Metric']
df = pd.DataFrame(columns=header)
df.to_csv(f'{measurement_directory}/datapoints.csv', mode='w', index=False, header=True)


# Create CSV file containing the current camera and measurement settings

measurement_metadata = return_camera_settings()
measurement_metadata['min intensity'] = min_intensity
measurement_metadata['max intensity'] = max_intensity
measurement_metadata['intensity increment'] = intensity_increment
measurement_metadata['averaged frames'] = averaged_frames
measurement_metadata['throwaway frames'] = throwaway_frames
measurement_metadata['minimum temperature'] = min_temp
measurement_metadata['maximum temperature'] = max_temp
measurement_metadata['temperature increment'] = temp_increment
measurement_metadata['type of measurement'] = type_of_measurement

df = pd.DataFrame.from_dict(measurement_metadata, orient='index', columns=['Value'])
df.to_csv(f'{measurement_directory}/measurement_metadata.csv', mode='w')


def set_temperature(temperature):
    with open('temp_setpoint.txt', 'w') as f:
        f.write(str(temperature))


# Run measurement

start_time = time.time()

for temp in range(min_temp, max_temp, temp_increment):
    print(f'Setting Temperature to {temp} °C...')
    set_temperature(temperature=temp)
    print('Waiting for temperature to be reached...\n')
    time.sleep(time_to_thermal_equil)

    for intensity in range(min_intensity, max_intensity, intensity_increment):
        print(f'    Measuring at intensity {intensity}...\n')
        set_led(intensity=intensity)
        time.sleep(led_response_time)

        measurement_start_time = time.time()
        frames = acquire_series_of_frames(averaged_frames + throwaway_frames)[throwaway_frames:]
        measurement_end_time = time.time()

        sum_of_frames = np.zeros(frames[0].shape, dtype=np.uint64)
        avrg_count_of_second_peak = 0

        for frame in frames:
            frame_bincount = np.bincount(frame.flatten())
            count_of_second_peak = sorted(frame_bincount)[-2]
            avrg_count_of_second_peak += count_of_second_peak

            np.add(sum_of_frames, frame, out=sum_of_frames)

        avrg_count_of_second_peak /= averaged_frames
        hist_metric = evaluate_signal(sum_of_frames)

        temperature_values = []
        temp_count = 0
        temp_mean = 0
        temp_min = np.inf
        temp_max = -np.inf

        with open('temp_log.txt', 'r') as f:
            for line in f:
                temperature_values.append(eval(line))

        for temperature_dict in temperature_values:
            if measurement_start_time < temperature_dict['timestamp'] < measurement_end_time:
                temperature_value = temperature_dict['probe']
                temp_mean += temperature_value
                temp_count += 1

                if temperature_value < temp_min:
                    temp_min = temperature_value

                if temperature_value > temp_max:
                    temp_max = temperature_value

        temp_mean /= temp_count

        norm_sum_of_clipped_frames = np.interp(sum_of_frames, (np.min(sum_of_frames), np.max(sum_of_frames)), (0, 255))
        img = Image.fromarray(norm_sum_of_clipped_frames).convert('L')
        img.save(f'{photo_directory}/temp-{temp_mean}_int-{intensity}.png')

        data_entry = [temp, temp_mean, temp_min, temp_max, intensity, avrg_count_of_second_peak, hist_metric]
        df = pd.DataFrame([data_entry])
        df.to_csv(f'{measurement_directory}/datapoints.csv', mode='a', index=False, header=False)

set_led(intensity=0)
set_temperature(temperature=0)

print(f'Done with measurement.\n'
      f'Estimated execution time was {timedelta(seconds=est_execution_time)} ( hh:mm:ss )\n'
      f'Actual execution time was {timedelta(seconds=time.time()-start_time)} ( hh:mm:ss )\n\n\n')
