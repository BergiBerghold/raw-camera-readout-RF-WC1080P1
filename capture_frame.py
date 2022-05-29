from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
from PIL import Image, ImagePalette
import numpy as np
import rawpy
import cv2
import io


def split_list(alist, n):
    length = len(alist)
    return [alist[i*length // n: (i+1)*length // n] for i in range(n)]


# Capture settings

number_of_frames = 1
resolution = 1920, 1080

# Camera settings
# Some effect

saturation = 40                                 # min=0 max=100 step=1 default=40
hue = 0                                          # min=-2000 max=2000 step=100 default=0
white_balance_temperature_auto = 1               # default=1
white_balance_temperature = 4600                 # min=2800 max=6500 step=1 default=4600
exposure_auto = 3                                # min=0 max=3 default=3 (1: Manual Mode / 3: Aperture Priority Mode)

# No effect

contrast = 35                                    # min=0 max=95 step=1 default=35
brightness = 135                                 # min=0 max=255 step=1 default=135
gamma = 140                                      # min=100 max=300 step=1 default=140
gain = 16                                        # min=16 max=255 step=1 default=16
power_line_frequency = 0                         # min=0 max=2 default=1 (0: Disabled / 1: 50 Hz / 2: 60 Hz)
sharpness = 5                                    # min=0 max=70 step=1 default=5
backlight_compensation = 64                       # min=8 max=200 step=1 default=64
exposure_absolute = 3                            # min=3 max=8192 step=1 default=500

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
       f'--stream-count={number_of_frames}',
       '--stream-to=-']

#process = Popen(cmd, stdout=PIPE, stderr=PIPE)
#stdout, stderr = process.communicate()

#raw_data = np.frombuffer(stdout, dtype=np.uint8, count=resolution[0] * resolution[1] * 2)
raw_data = np.fromfile('file0.raw', dtype=np.uint8, count=resolution[0] * resolution[1] * 2)
yuv_array = raw_data.reshape(resolution[1], resolution[0], 2)

rgb_array = cv2.cvtColor(yuv_array, cv2.COLOR_YUV2RGB_YUYV)


y_channel = yuv_array[:,:,0]

u_channel = np.copy(yuv_array[:,:,1])
u_channel[:,1::2] = u_channel[:,0::2]

v_channel = np.copy(yuv_array[:,:,1])
v_channel[:,0::2] = v_channel[:,1::2]


plt.imshow(y_channel, cmap='gray')
plt.title('Y Channel')
plt.show()

plt.imshow(u_channel, cmap='gray')
plt.title('U Channel')
plt.show()

plt.imshow(v_channel, cmap='gray')
plt.title('V Channel')
plt.show()

plt.imshow(rgb_array, cmap='gray')
plt.title('RGB Converted')
plt.show()

Image.fromarray(v_channel).save('v_ch.png')
