from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
import rawpy
import io

brightness = 135                                   # min=0 max=255 step=1 default=135
contrast = 35                                     # min=0 max=95 step=1 default=35
saturation = 100                                 # min=0 max=100 step=1 default=40
hue = 0                                          # min=-2000 max=2000 step=100 default=0
white_balance_temperature_auto = 0               # default=1
white_balance_temperature = 4600                 # min=2800 max=6500 step=1 default=4600
gamma = 140                                      # min=100 max=300 step=1 default=140
gain = 255                                       # min=16 max=255 step=1 default=16
power_line_frequency = 0                         # min=0 max=2 default=1 (0: Disabled / 1: 50 Hz / 2: 60 Hz)
sharpness = 5                                    # min=0 max=70 step=1 default=5
backlight_compensation = 64                       # min=8 max=200 step=1 default=64
exposure_auto = 1                                 # min=0 max=3 default=3 (1: Manual Mode / 3: Aperture Priority Mode)
exposure_absolute = 8192                          # min=3 max=8192 step=1 default=500

cmd = ['ssh',
       'experiment',
       'v4l2-ctl',
       '--device=/dev/video4',

       '--set-fmt-video=' +
       f'width={1920},' +
       f'height={1080},' +
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
       '--stream-count=1',
       '--stream-to=-']

process = Popen(cmd, stdout=PIPE, stderr=PIPE)
stdout, stderr = process.communicate()

img = rawpy.imread(io.BytesIO(stdout))

img_monochrome = img.raw_image_visible

print(img_monochrome[50,50])

plt.imshow(img_monochrome, cmap='gray', interpolation=None)
plt.show()