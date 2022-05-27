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

process = Popen(cmd, stdout=PIPE, stderr=PIPE)
stdout, stderr = process.communicate()

raw_data = np.frombuffer(stdout, dtype=np.uint8, count=resolution[0] * resolution[1] * 2)
print(len(raw_data))
im = raw_data.reshape(resolution[1], resolution[0], 2)

#rgb = cv2.cvtColor(im, cv2.COLOR_YUV2RGB_YUYV)

plt.imshow(im[:,:,1])
plt.title('CV2')
plt.show()




with rawpy.imread(io.BytesIO(stdout)) as img:
    img_monochrome = np.copy(img.raw_image_visible)

plt.imshow(img_monochrome)
plt.title('RAWPY')
plt.show()


exit()

frames = split_list(stdout, number_of_frames)
sum_of_frames = np.zeros(resolution[::-1])

for n, frame in enumerate(frames):
    with rawpy.imread(io.BytesIO(frame)) as img:
        img_monochrome = np.copy(img.raw_image_visible)
        bayer_filter = np.copy(img.raw_colors)

        sum_of_frames += img_monochrome

        #print(f'Minimum: {np.min(img_monochrome)}')
        #print(f'Maximum: {np.max(img_monochrome)}')

        #plt.imshow(img_monochrome, cmap='gray', interpolation=None, resample=False) #, vmin=0, vmax=65535)
        #plt.title(f'Frame No. {n+1}')
        #plt.show()

bayer_filter = np.stack([bayer_filter, np.zeros(bayer_filter.shape), np.zeros(bayer_filter.shape)], axis=2)

bayer_filter[bayer_filter[:,:,0] == 0] = [255, 0, 0]        # Red
bayer_filter[bayer_filter[:,:,0] == 1] = [0, 255, 0]        # Green 1
bayer_filter[bayer_filter[:,:,0] == 2] = [0, 0, 255]        # Blue
bayer_filter[bayer_filter[:,:,0] == 3] = [0, 255, 0]        # Green 2


img_monochrome = np.interp(img_monochrome, [np.min(img_monochrome), np.max(img_monochrome)], [0, 1])

new_array = bayer_filter * np.repeat(img_monochrome[:, :, np.newaxis], 3, axis=2)
new_array = new_array.astype(np.uint8)

plt.imshow(new_array)
plt.show()

Image.fromarray(new_array).save('sum1.png')




exit()

plt.imshow(sum_of_frames, cmap='gray', interpolation=None, resample=False) #, vmin=0, vmax=65535)
plt.title('Sum of all Frames')
plt.show()

bayer_color_palette = [255,0,0, 0,255,0, 0,0,255, 0,255,0]

bayer_filter_img = Image.fromarray(bayer_filter, mode='P')
bayer_filter_img.putpalette(bayer_color_palette, rawmode='RGB')
bayer_filter_img = bayer_filter_img.convert("RGB")

sum_of_frames_normalized = np.interp(sum_of_frames, [np.min(sum_of_frames), np.max(sum_of_frames)], [0, 255])
normalized_monochrome_img = Image.fromarray(sum_of_frames_normalized).convert("RGB")

Image.blend(bayer_filter_img, normalized_monochrome_img, 0.8).save('sum1.png')