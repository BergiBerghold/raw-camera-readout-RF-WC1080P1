from photon_calculator import calculate_flux
from evaluate_signal import evaluate_signal
from temperature_controller import *
from subprocess import Popen, PIPE
from led_driver import set_led
import matplotlib.pyplot as plt
import matplotlib.colors as colr
from PIL import Image
import numpy as np
import time
import cv2
import os


# Capture settings
resolution = 1920, 1080

# Camera settings
# Some effect

brightness = 255                                 # min=0 max=255 step=1 default=135
contrast = 95                                    # min=0 max=95 step=1 default=35
white_balance_temperature_auto = 0               # default=1
white_balance_temperature = 4600                 # min=2800 max=6500 step=1 default=4600
exposure_auto = 3                                # min=0 max=3 default=3 (1: Manual Mode / 3: Aperture Priority Mode)
gain = 255                                        # min=16 max=255 step=1 default=16

# No effect

saturation = 40                                 # min=0 max=100 step=1 default=40
hue = 0                                          # min=-2000 max=2000 step=100 default=0
power_line_frequency = 0                         # min=0 max=2 default=1 (0: Disabled / 1: 50 Hz / 2: 60 Hz)
backlight_compensation = 200                       # min=8 max=200 step=1 default=64
exposure_absolute = 8192                            # min=3 max=8192 step=1 default=500
gamma = 300                                      # min=100 max=300 step=1 default=140
sharpness = 0                                    # min=0 max=70 step=1 default=5


def acquire_sum_of_frames(n_frames=1, display=False, save=False, save_raw=False, print_stderr=False, run_local=False,
                          override_brightness=brightness, override_gain=gain, video_device=4):
    v4l2_cmd = ['ssh',
                'experiment',
                'v4l2-ctl',
                f'--device=/dev/video{video_device}',

                '--set-fmt-video=' +
                f'width={resolution[0]},' +
                f'height={resolution[1]},' +
                'pixelformat=YUYV',

                '--set-ctrl=' +
                f'brightness={override_brightness},' +
                f'contrast={contrast},' +
                f'saturation={saturation},' +
                f'hue={hue},' +
                f'white_balance_temperature_auto={white_balance_temperature_auto},' +
                f'gamma={gamma},' +
                f'gain={override_gain},' +
                f'power_line_frequency={power_line_frequency},' +
                f'white_balance_temperature={white_balance_temperature},' +
                f'sharpness={sharpness},' +
                f'backlight_compensation={backlight_compensation},' +
                f'exposure_auto={exposure_auto},' +
                f'exposure_absolute={exposure_absolute}',

                '--stream-mmap',
                f'--stream-count={n_frames}',
                '--stream-to=-']

    if os.getenv('CCD_MACHINE') or run_local:
        v4l2_cmd = v4l2_cmd[2:]

    v4l2_process = Popen(v4l2_cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = v4l2_process.communicate()

    if stderr[:-3] and print_stderr:
        print(f'Stderr not empty: {stderr.decode()}')

    if save_raw:
        with open('img.raw', 'wb') as f:
            f.write(stdout)

    raw_data = np.frombuffer(stdout, dtype=np.uint8)
    # raw_data = np.fromfile('img.raw', dtype=np.uint8)
    yuv_frames_array = raw_data.reshape(n_frames, resolution[1], resolution[0], 2)

    sum_of_y_channel = np.zeros((resolution[1], resolution[0]), dtype=np.uint32)
    sum_of_u_channel = np.zeros((resolution[1], resolution[0]), dtype=np.uint32)
    sum_of_v_channel = np.zeros((resolution[1], resolution[0]), dtype=np.uint32)

    for yuv_frame in yuv_frames_array:
        rgb_array = cv2.cvtColor(yuv_frame, cv2.COLOR_YUV2RGB_YUYV)

        y_channel = yuv_frame[:,:,0]

        u_channel = np.copy(yuv_frame[:,:,1])
        u_channel[:,1::2] = u_channel[:,0::2]

        v_channel = np.copy(yuv_frame[:,:,1])
        v_channel[:,0::2] = v_channel[:,1::2]

        sum_of_y_channel += y_channel
        sum_of_u_channel += u_channel
        sum_of_v_channel += v_channel

    if display:
        fig, ax = plt.subplots()

        plt.subplot(2, 2, 1)
        plt.imshow(sum_of_y_channel, cmap='gray') #, norm=colr.Normalize(vmin=800, vmax=1500, clip=False))
        plt.title(f'Sum of {n_frames} Frames (Y)')
        plt.xlabel(f'min.: {np.min(sum_of_y_channel)}/max.: {np.max(sum_of_y_channel)}')

        plt.subplot(2, 2, 2)
        plt.imshow(sum_of_u_channel, cmap='gray')
        plt.title(f'Sum of {n_frames} Frames (U)')
        plt.xlabel(f'min.: {np.min(sum_of_u_channel)}/max.: {np.max(sum_of_u_channel)}')

        plt.subplot(2, 2, 3)
        plt.imshow(sum_of_v_channel, cmap='gray')
        plt.title(f'Sum of {n_frames} Frames (V)')
        plt.xlabel(f'min.: {np.min(sum_of_v_channel)}/max.: {np.max(sum_of_v_channel)}')

        # plt.subplot(2, 2, 4)
        # plt.imshow(rgb_array)
        # plt.title(f'Sum of {n_frames} Frames (RGB)')
        # plt.xlabel(f'min.: {np.min(rgb_array)}/max.: {np.max(rgb_array)}')

        plt.subplot(2, 2, 4)
        plt.hist(sum_of_y_channel.flatten(), bins=max((min(int(np.max(sum_of_y_channel)), 2000)), 1))
        plt.semilogy()
        plt.title('Histogram of Y Channel')

        fig.set_size_inches(14, 14)
        plt.show()

    if save:
        normalized_sum_of_y_channel = np.interp(sum_of_y_channel, (np.min(sum_of_y_channel), np.max(sum_of_y_channel)), (0, 255))
        #normalized_sum_of_y_channel = np.interp(sum_of_y_channel, (800, 1500), (0, 255))
        Image.fromarray(normalized_sum_of_y_channel).convert('L').save('sum_y.png')

        normalized_sum_of_u_channel = np.interp(sum_of_u_channel, (np.min(sum_of_u_channel), np.max(sum_of_u_channel)), (0, 255))
        Image.fromarray(normalized_sum_of_u_channel).convert('L').save('sum_u.png')

        normalized_sum_of_v_channel = np.interp(sum_of_v_channel, (np.min(sum_of_v_channel), np.max(sum_of_v_channel)), (0, 255))
        Image.fromarray(normalized_sum_of_v_channel).convert('L').save('sum_v.png')

    return sum_of_y_channel, sum_of_u_channel, sum_of_v_channel


def acquire_series_of_frames(n_frames=1, print_stderr=False, return_stderr=False, override_brightness=brightness,
                             override_gain=gain, override_exposure=exposure_absolute, override_wbt=white_balance_temperature):
    v4l2_cmd = ['ssh',
                'experiment',
                'v4l2-ctl',
                '--device=/dev/video4',

                '--set-fmt-video=' +
                f'width={resolution[0]},' +
                f'height={resolution[1]},' +
                'pixelformat=YUYV',

                '--set-ctrl=' +
                f'brightness={override_brightness},' +
                f'contrast={contrast},' +
                f'saturation={saturation},' +
                f'hue={hue},' +
                f'white_balance_temperature_auto={white_balance_temperature_auto},' +
                f'gamma={gamma},' +
                f'gain={override_gain},' +
                f'power_line_frequency={power_line_frequency},' +
                f'white_balance_temperature={override_wbt},' +
                f'sharpness={sharpness},' +
                f'backlight_compensation={backlight_compensation},' +
                f'exposure_auto={exposure_auto},' +
                f'exposure_absolute={override_exposure}',

                '--stream-mmap',
                f'--stream-count={n_frames}',
                '--stream-to=-']

    if os.getenv('CCD_MACHINE'):
        v4l2_cmd = v4l2_cmd[2:]

    v4l2_process = Popen(v4l2_cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = v4l2_process.communicate()

    if stderr[:-3] and print_stderr:
        print(f'Stderr not empty: {stderr.decode()}')

    raw_data = np.frombuffer(stdout, dtype=np.uint8)
    yuv_frames_array = raw_data.reshape(n_frames, resolution[1], resolution[0], 2)

    y_channel_frames_array = np.copy(yuv_frames_array[:, :, :, 0])

    del yuv_frames_array

    if return_stderr:
        return y_channel_frames_array, stderr.decode()
    else:
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
    acquire_sum_of_frames(save=True, run_local=True, video_device=4)


