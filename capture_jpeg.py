from photon_calculator import calculate_flux
from subprocess import Popen, PIPE
from led_driver import set_led
import matplotlib.pyplot as plt
import matplotlib.colors as colr
from io import BytesIO
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


def acquire_sum_of_frames(n_frames=1, display=False, save=False, save_raw=False, print_stderr=True,
                          override_brightness=brightness, override_gain=gain, video_device=4):
    v4l2_cmd = ['ssh',
                'experiment',
                'v4l2-ctl',
                f'--device=/dev/video{video_device}',

                '--set-fmt-video=' +
                f'width={resolution[0]},' +
                f'height={resolution[1]},' +
                'pixelformat=MJPG',

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

    if os.getenv('CCD_MACHINE'):
        v4l2_cmd = v4l2_cmd[2:]

    v4l2_process = Popen(v4l2_cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = v4l2_process.communicate()

    if stderr[:-3] and print_stderr:
        print(f'Stderr not empty: {stderr.decode()}')

    frames = [x + b'\xff\xd9' for x in stdout.split(b'\xff\xd9')][:-1]

    for frame in frames:
        img = np.array(Image.open(BytesIO(frame)))

        fig, ax = plt.subplots()

        plt.subplot(3, 2, 1)
        plt.imshow(img)
        plt.title('RGB Image')

        plt.subplot(3, 2, 3)
        r_channel = img[:,:,0]
        plt.hist(r_channel.flatten(), bins=max((min(int(np.max(r_channel)), 2000)), 1))
        plt.semilogy()
        plt.title('Histogram of R Channel')

        plt.subplot(3, 2, 4)
        g_channel = img[:, :, 1]
        plt.hist(g_channel.flatten(), bins=max((min(int(np.max(g_channel)), 2000)), 1))
        plt.semilogy()
        plt.title('Histogram of G Channel')

        plt.subplot(3, 2, 5)
        b_channel = img[:, :, 2]
        plt.hist(b_channel.flatten(), bins=max((min(int(np.max(b_channel)), 2000)), 1))
        plt.semilogy()
        plt.title('Histogram of B Channel')

        bincount = np.bincount(r_channel.flatten())
        mfv = bincount.argmax()
        r_clipped = np.zeros(r_channel.shape)
        r_clipped[r_channel > mfv] = 1

        bincount = np.bincount(g_channel.flatten())
        mfv = bincount.argmax()
        g_clipped = np.zeros(g_channel.shape)
        g_clipped[g_channel > mfv] = 1

        bincount = np.bincount(b_channel.flatten())
        mfv = bincount.argmax()
        b_clipped = np.zeros(b_channel.shape)
        b_clipped[b_channel > mfv] = 1

        rgb_clipped = np.stack((r_clipped, g_clipped, b_clipped), 2)

        plt.subplot(3, 2, 2)
        plt.imshow(rgb_clipped)
        plt.title('Clipped RGB Image')

        fig.set_size_inches(9, 9)
        plt.show()


acquire_sum_of_frames(n_frames=15)
