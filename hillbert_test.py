import matplotlib.pyplot as plt
import numpy as np
import time


def reverse_in_bin(x, n_bits=8):
    binary = bin(x)[2:].zfill(n_bits)
    reversed_binary = binary[::-1]

    return int(reversed_binary, 2)


heatmap_array = np.zeros((1024, 1024), dtype=bool)
plt.imshow(heatmap_array)
plt.show()

for i in range(1024**2):
    f = reverse_in_bin(i, n_bits=20)
    f = bin(f)[2:].zfill(20)

    x = int(f[::2], 2)
    y = int(f[1::2], 2)

    print(x,y)

    heatmap_array[x, y] = 1

    plt.imshow(heatmap_array)
    plt.show()

    time.sleep(0.01)



