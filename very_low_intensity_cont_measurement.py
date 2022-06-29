from capture_frame import acquire_series_of_frames, return_camera_settings
from photon_calculator import calculate_flux
from subprocess import Popen, PIPE
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

run_time = 180
camera_fps = 4
led_increase_interval = 5
led_increase_steps = 0
frames = run_time * camera_fps
max_intensity = int(run_time / led_increase_interval * led_increase_steps)


# Calculate and print execution time

print(f'Measuring for {run_time} seconds\n'
      f'LED Brightness will go from 0 to {max_intensity}')

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

header = ['Second Peak Count']
df = pd.DataFrame(columns=header)
df.to_csv(f'{measurement_directory}/datapoints.csv', mode='w', index=False, header=True)


# Camera Settings

resolution = 1920, 1080

brightness = 255                                 # min=0 max=255 step=1 default=135
contrast = 95                                    # min=0 max=95 step=1 default=35
gamma = 300                                      # min=100 max=300 step=1 default=140
sharpness = 0                                    # min=0 max=70 step=1 default=5
white_balance_temperature_auto = 0               # default=1
white_balance_temperature = 2300                 # min=2800 max=6500 step=1 default=4600
exposure_auto = 1                                # min=0 max=3 default=3 (1: Manual Mode / 3: Aperture Priority Mode)
gain = 255                                        # min=16 max=255 step=1 default=16

# No effect

saturation = 40                                 # min=0 max=100 step=1 default=40
hue = 0                                          # min=-2000 max=2000 step=100 default=0
power_line_frequency = 0                         # min=0 max=2 default=1 (0: Disabled / 1: 50 Hz / 2: 60 Hz)
backlight_compensation = 64                       # min=8 max=200 step=1 default=64
exposure_absolute = 8192                            # min=3 max=8192 step=1 default=500

v4l2_cmd = ['ssh',
            'experiment',
            'v4l2-ctl',
            '--device=/dev/video4',

            '--set-fmt-video=' +
            f'width={resolution[0]},' +
            f'height={resolution[1]},' +
            'pixelformat=YUYV',

            '--set-ctrl=' +
            f'brightness={brightness},' +
            f'contrast={contrast},' +
            f'saturation={saturation},' +
            f'hue={hue},' +
            f'white_balance_temperature_auto={white_balance_temperature_auto},' +
            f'gamma={gamma},' +
            f'gain={gain},' +
            f'power_line_frequency={power_line_frequency},' +
            f'white_balance_temperature={white_balance_temperature},' +
            f'sharpness={sharpness},' +
            f'backlight_compensation={backlight_compensation},' +
            f'exposure_auto={exposure_auto},' +
            f'exposure_absolute={exposure_absolute}',

            '--stream-mmap',
            f'--stream-count={frames}',
            '--stream-to=-']

if os.getenv('CCD_MACHINE'):
    v4l2_cmd = v4l2_cmd[2:]


# Create CSV file containing the current camera and measurement settings

settings = {'width': resolution[0],
            'height': resolution[1],
            'brightness': brightness,
            'contrast': contrast,
            'gamma': gamma,
            'white_balance_temperature_auto': white_balance_temperature_auto,
            'white_balance_temperature': white_balance_temperature,
            'exposure_auto': exposure_auto,
            'hue': hue,
            'saturation': saturation,
            'gain': gain,
            'power_line_frequency': power_line_frequency,
            'sharpness': sharpness,
            'backlight_compensation': backlight_compensation,
            'exposure_absolute': exposure_absolute}

measurement_metadata = settings

measurement_metadata['run time'] = run_time
measurement_metadata['frames'] = frames
measurement_metadata['max intensity'] = max_intensity
measurement_metadata['led increase steps'] = led_increase_steps
measurement_metadata['led increase interval'] = led_increase_interval
measurement_metadata['type of measurement'] = type_of_measurement

df = pd.DataFrame.from_dict(measurement_metadata, orient='index', columns=['Value'])
df.to_csv(f'{measurement_directory}/measurement_metadata.csv', mode='w')


# Run measurement

start_time = time.perf_counter()

led_intensity_counter = 0
set_led(intensity=0)
v4l2_process = Popen(v4l2_cmd, stdout=PIPE, stderr=PIPE)

while True:
    curr_time = time.perf_counter()

    if (curr_time - start_time) % led_increase_steps < 10**(-3):
        led_intensity_counter += led_increase_interval
        set_led(intensity=led_intensity_counter)
        print(f'    Setting LED to {led_intensity_counter}...')

    if curr_time - start_time > run_time:
        break

stdout, stderr = v4l2_process.communicate()
raw_data = np.frombuffer(stdout, dtype=np.uint8)
yuv_frames_array = raw_data.reshape(frames, resolution[1], resolution[0], 2)

y_channel_frames_array = np.copy(yuv_frames_array[:, :, :, 0])
del yuv_frames_array

for frame in y_channel_frames_array:
    frame_bincount = np.bincount(frame.flatten())
    count_of_second_peak = sorted(frame_bincount)[-2]

    data_entry = [count_of_second_peak]
    df = pd.DataFrame([data_entry])
    df.to_csv(f'{measurement_directory}/datapoints.csv', mode='a', index=False, header=False)


print(f'Done with measurement.\n'
      f'Actual execution time was {timedelta(seconds=time.perf_counter()-start_time)} ( hh:mm:ss )\n\n\n')
