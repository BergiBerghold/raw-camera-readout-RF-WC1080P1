from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import cv2
import os


# Capture settings
resolution = 1920, 1080

# Camera settings
# Some effect

brightness = 135                                 # min=0 max=255 step=1 default=135
contrast = 95                                    # min=0 max=95 step=1 default=35
gamma = 140                                      # min=100 max=300 step=1 default=140
white_balance_temperature_auto = 0               # default=1
white_balance_temperature = 4600                 # min=2800 max=6500 step=1 default=4600
exposure_auto = 3                                # min=0 max=3 default=3 (1: Manual Mode / 3: Aperture Priority Mode)

# No effect

hue = 0                                          # min=-2000 max=2000 step=100 default=0
saturation = 40                                 # min=0 max=100 step=1 default=40
gain = 16                                        # min=16 max=255 step=1 default=16
power_line_frequency = 0                         # min=0 max=2 default=1 (0: Disabled / 1: 50 Hz / 2: 60 Hz)
sharpness = 5                                    # min=0 max=70 step=1 default=5
backlight_compensation = 64                       # min=8 max=200 step=1 default=64
exposure_absolute = 3                            # min=3 max=8192 step=1 default=500


def acquire_sum_of_frames(n_frames=1, display=False, save=False):
    cmd = ['ssh',
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
           f'--stream-count={n_frames}',
           '--stream-to=.temp']

    if os.getenv('CCD_MACHINE'):
        cmd = cmd[2:]

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    if stderr[:-3]:
        print(f'Stderr not empty: {stderr}')

    raw_data = np.fromfile('.temp', dtype=np.uint8)
    yuv_frames_array = raw_data.reshape(n_frames, resolution[1], resolution[0], 2)

    os.remove('.temp')

    sum_of_y_channel = np.zeros((resolution[1], resolution[0]))
    sum_of_u_channel = np.zeros((resolution[1], resolution[0]))
    sum_of_v_channel = np.zeros((resolution[1], resolution[0]))

    for yuv_frame in yuv_frames_array:
        #rgb_array = cv2.cvtColor(yuv_frame, cv2.COLOR_YUV2RGB_YUYV)

        y_channel = yuv_frame[:,:,0]

        u_channel = np.copy(yuv_frame[:,:,1])
        u_channel[:,1::2] = u_channel[:,0::2]

        v_channel = np.copy(yuv_frame[:,:,1])
        v_channel[:,0::2] = v_channel[:,1::2]

        sum_of_y_channel += y_channel
        sum_of_u_channel += u_channel
        sum_of_v_channel += v_channel

    if display:
        plt.imshow(sum_of_y_channel, cmap='gray')
        plt.title(f'Sum of {n_frames} Frames (Y)')
        plt.xlabel(f'max. Value: {np.max(sum_of_y_channel)}')
        plt.show()

        plt.imshow(sum_of_u_channel, cmap='gray')
        plt.title(f'Sum of {n_frames} Frames (U)')
        plt.show()

        plt.imshow(sum_of_v_channel, cmap='gray')
        plt.title(f'Sum of {n_frames} Frames (V)')
        plt.show()

    if save:
        normalized_sum_of_y_channel = np.interp(sum_of_y_channel, (np.min(sum_of_y_channel), np.max(sum_of_y_channel)), (0, 255))
        #normalized_sum_of_y_channel = sum_of_y_channel / n_frames
        Image.fromarray(normalized_sum_of_y_channel).convert('L').save('sum_y.png')

        normalized_sum_of_u_channel = np.interp(sum_of_u_channel, (np.min(sum_of_u_channel), np.max(sum_of_u_channel)), (0, 255))
        #normalized_sum_of_u_channel = sum_of_u_channel / n_frames
        Image.fromarray(normalized_sum_of_u_channel).convert('L').save('sum_u.png')

        normalized_sum_of_v_channel = np.interp(sum_of_v_channel, (np.min(sum_of_v_channel), np.max(sum_of_v_channel)), (0, 255))
        #normalized_sum_of_v_channel = sum_of_v_channel / n_frames
        Image.fromarray(normalized_sum_of_v_channel).convert('L').save('sum_v.png')

    return sum_of_y_channel, sum_of_u_channel, sum_of_v_channel


def acquire_series_of_frames(n_frames=1):
    cmd = ['ssh',
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
           f'--stream-count={n_frames}',
           '--stream-to=.temp']

    if os.getenv('CCD_MACHINE'):
        cmd = cmd[2:]

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    if stderr[:-3]:
        print(f'Stderr not empty: {stderr}')

    raw_data = np.fromfile('.temp', dtype=np.uint8)
    yuv_frames_array = raw_data.reshape(n_frames, resolution[1], resolution[0], 2)

    os.remove('.temp')

    y_channel_frames_array = yuv_frames_array[:, :, :, 0]

    return y_channel_frames_array


def return_camera_settings():
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

    return settings


if __name__ == '__main__':
    acquire_series_of_frames(1)
