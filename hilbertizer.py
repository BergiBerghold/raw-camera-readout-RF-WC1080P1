import matplotlib.pyplot as plt
import numpy as np
import time


def reverse_in_bin(x, n_bits=8):
    binary = bin(x)[2:].zfill(n_bits)
    reversed_binary = binary[::-1]

    return int(reversed_binary, 2)


if __name__ == '__main__':
    heatmap_array = np.zeros((256, 256), dtype=bool)

    fig, ax = plt.subplots(1, 1)
    im = ax.imshow(heatmap_array, vmin=0, vmax=1)

    for i in range(256**2):
        f = reverse_in_bin(i, n_bits=16)
        f = bin(f)[2:].zfill(16)

        x = int(f[::2], 2)
        y = int(f[1::2], 2)

        heatmap_array[x, y] = 1

        im.set_data(heatmap_array)
        fig.canvas.draw_idle()
        plt.pause(0.00001)