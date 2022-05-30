from photon_calculator import calculate_flux
from capture_frame import do_capture
from led_driver import set_led
import numpy as np
import time


frames = 5

for intensity in range(0, 65536, 20000):
    set_led(intensity=intensity)
    photon_flux = calculate_flux(intensity)

    time.sleep(4)

    sum_of_y_channel, _, _ = do_capture(n_frames=frames)

    sum_of_y_channel /= frames

    print(photon_flux, np.average(sum_of_y_channel))