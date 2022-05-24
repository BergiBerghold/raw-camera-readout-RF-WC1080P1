import numpy as np
import rawpy
import matplotlib.pyplot as plt
import io


def split_list(alist, n):
    length = len(alist)
    return [alist[i*length // n: (i+1)*length // n] for i in range(n)]


with open('/Users/bergi/test_m/file.raw', 'rb') as f:
    data = f.read()

data = split_list(data, 3)[0]
img = rawpy.imread(io.BytesIO(data))

img_monochrome = img.raw_image_visible

plt.imshow(img_monochrome, cmap='gray', interpolation=None)
plt.show()

exit()



img_proc = img.postprocess()
img_proc = img_proc.reshape(1080*1920, 3)

for chanel, color in zip(np.transpose(img_proc), ['red', 'blue', 'green']):
    histogram, edges = np.histogram(chanel, bins=265)

    lower = None
    upper = None

    plt.plot(range(len(histogram))[lower:upper], histogram[lower:upper], color=color)

plt.show()