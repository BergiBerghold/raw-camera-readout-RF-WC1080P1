import matplotlib.pyplot as plt
import numpy as np
import time


def reverse_in_bin(x, n_bits=8):
    binary = bin(x)[2:].zfill(n_bits)
    reversed_binary = binary[::-1]

    return int(reversed_binary, 2)


# plt.ion()
#
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
#
# ax.set_xlim(0,255)
# ax.set_ylim(0,255)
# ax.set_zlim(0,255)
#
# A_x = []
# A_y = []
# A_z = []
#
# im = ax.scatter(A_x, A_y, A_z)
# fig.show()
#
#
#
# for i in range(256**3):
#     f = reverse_in_bin(i, n_bits=24)
#     f = bin(f)[2:].zfill(24)
#
#     x = int(f[0::3], 2)
#     y = int(f[1::3], 2)
#     z = int(f[2::3], 2)
#
#     print(x,y,z)
#
#     im = ax.scatter([x], [y], [z], color='blue')
#     plt.draw()
#     plt.pause(0.001)



heatmap_array = np.zeros((256, 256), dtype=bool)

fig, ax = plt.subplots(1, 1)
im = ax.imshow(heatmap_array, vmin=0, vmax=1)

input('Go?')

for i in range(256**2):
    f = reverse_in_bin(i, n_bits=16)
    f = bin(f)[2:].zfill(16)

    x = int(f[::2], 2)
    y = int(f[1::2], 2)

    heatmap_array[x, y] = 1

    im.set_data(heatmap_array)
    fig.canvas.draw_idle()
    plt.pause(0.00001)