from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
import numpy as np
import rawpy
import io


def split_list(alist, n):
    length = len(alist)
    return [alist[i*length // n: (i+1)*length // n] for i in range(n)]


# Capture settings

number_of_frames = 5
resolution = 1920, 1080

# Camera settings
# Some effect

saturation = 100                                 # min=0 max=100 step=1 default=40
hue = 0                                          # min=-2000 max=2000 step=100 default=0
white_balance_temperature_auto = 0               # default=1
white_balance_temperature = 4600                 # min=2800 max=6500 step=1 default=4600
exposure_auto = 3                                # min=0 max=3 default=3 (1: Manual Mode / 3: Aperture Priority Mode)

# No effect

contrast = 95                                    # min=0 max=95 step=1 default=35
brightness = 255                                 # min=0 max=255 step=1 default=135
gamma = 100                                      # min=100 max=300 step=1 default=140
gain = 16                                        # min=16 max=255 step=1 default=16
power_line_frequency = 0                         # min=0 max=2 default=1 (0: Disabled / 1: 50 Hz / 2: 60 Hz)
sharpness = 0                                    # min=0 max=70 step=1 default=5
backlight_compensation = 8                       # min=8 max=200 step=1 default=64
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

process = Popen(cmd, stdout=PIPE, stderr=PIPE)
stdout, stderr = process.communicate()

frames = split_list(stdout, number_of_frames)
sum_of_frames = np.zeros(resolution[::-1])

for n, frame in enumerate(frames):
    with rawpy.imread(io.BytesIO(frame)) as img:
        img_monochrome = img.raw_image_visible
        sum_of_frames += img_monochrome

        #print(f'Minimum: {np.min(img_monochrome)}')
        #print(f'Maximum: {np.max(img_monochrome)}')

        #plt.imshow(img_monochrome, cmap='gray', interpolation=None, resample=False) #, vmin=0, vmax=65535)
        #plt.title(f'Frame No. {n+1}')
        #plt.show()

plt.imshow(sum_of_frames, cmap='gray', interpolation=None, resample=False) #, vmin=0, vmax=65535)
plt.title('Sum of all Frames')
plt.savefig('sum.png', format="png", dpi=1000)