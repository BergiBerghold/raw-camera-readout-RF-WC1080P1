from capture_frame import acquire_series_of_frames, return_camera_settings
from photon_calculator import calculate_flux
from hilbertizer import reverse_in_bin
from datetime import datetime, timedelta
from led_driver import set_led
from PIL import Image
import pandas as pd
import numpy as np
import time
import sys
import os


# User Settings

intensity = 1000
whitebalance_temp = 2800    # min=2800 max=6500 step=1 default=4600
measurements = 50
led_response_time = 5
averaged_frames = 30
throwaway_frames = 10
gain = 255
brightness = 255


# Calculate and print execution time

camera_fps = 4
est_execution_time = measurements * (averaged_frames + throwaway_frames) / camera_fps

print(f'Doing {measurements} measurements with {averaged_frames} averaged frames '
      f'and {throwaway_frames} throwaway frames.\n'
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

header = ['Time Passed', 'Second Peak Count']
df = pd.DataFrame(columns=header)
df.to_csv(f'{measurement_directory}/datapoints.csv', mode='w', index=False, header=True)


# Create CSV file containing the current camera and measurement settings

measurement_metadata = return_camera_settings()
measurement_metadata['override brightness'] = brightness
measurement_metadata['override gain'] = gain
measurement_metadata['override wbt'] = whitebalance_temp
measurement_metadata['averaged frames'] = averaged_frames
measurement_metadata['throwaway frames'] = throwaway_frames
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
    time_of_measurement = time.perf_counter() - start_time
    frames = acquire_series_of_frames(averaged_frames + throwaway_frames, override_gain=gain,
                                      override_brightness=brightness, override_wbt=whitebalance_temp)[throwaway_frames:]

    avrg_count_of_second_peak = 0
    sum_of_clipped_frames = np.zeros(frames[0].shape, dtype=np.uint64)

    for frame in frames:
        frame_bincount = np.bincount(frame.flatten())
        count_of_second_peak = sorted(frame_bincount)[-2]
        avrg_count_of_second_peak += count_of_second_peak

        most_frequent_value = frame_bincount.argmax()
        clipped_frame = np.zeros(frame.shape, dtype=np.uint8)
        clipped_frame[frame > most_frequent_value] = 1
        np.add(sum_of_clipped_frames, clipped_frame, out=sum_of_clipped_frames)

    avrg_count_of_second_peak /= averaged_frames

    norm_sum_of_clipped_frames = np.interp(sum_of_clipped_frames, (np.min(sum_of_clipped_frames), np.max(sum_of_clipped_frames)), (0, 255))
    img = Image.fromarray(norm_sum_of_clipped_frames).convert('L')
    img.save(f'{photo_directory}/point-{point}.png')

    data_entry = [time_of_measurement, avrg_count_of_second_peak]
    df = pd.DataFrame([data_entry])
    df.to_csv(f'{measurement_directory}/datapoints.csv', mode='a', index=False, header=False)

set_led(intensity=0)

print(f'Done with measurement.\n'
      f'Estimated execution time was {timedelta(seconds=est_execution_time)} ( hh:mm:ss )\n'
      f'Actual execution time was {timedelta(seconds=time.perf_counter() - start_time)} ( hh:mm:ss )\n\n\n')