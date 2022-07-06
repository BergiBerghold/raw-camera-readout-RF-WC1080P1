from PIL import Image
import numpy as np


def calculate_euclidean_dist(img_array, clip_mfv=False):
    reference_img = np.asarray(Image.open('signal_to_noise_reference.png'))

    if clip_mfv:
        bincount = np.bincount(img_array.flatten())
        mfv = bincount.argmax()

        clipped_frame = np.zeros(img_array.shape)
        clipped_frame[img_array > mfv] = 255

        img_array = clipped_frame

    dist_euclidean = np.sqrt(np.sum((reference_img - img_array)**2)) / reference_img.size
    return dist_euclidean


if __name__ == '__main__':
    a = calculate_euclidean_dist(np.asarray(Image.open('point-4.png')))
    print(a)