from PIL import Image, ImageFilter
import matplotlib.pyplot as plt
import numpy as np


def evaluate_signal(array, plot_hist=False):
    mask = np.load('eval_signal_reference/mask.npy')

    pixelgroup_1 = array[mask == 1].flatten()
    pixelgroup_2 = array[mask == 2].flatten()

    m1 = np.mean(pixelgroup_1)
    m2 = np.mean(pixelgroup_2)

    s1 = np.std(pixelgroup_1)
    s2 = np.std(pixelgroup_2)

    metric = abs(m1 - m2) / np.sqrt(s1**2 + s2**2)

    if plot_hist:
        fig, ax = plt.subplots()

        plt.subplot(2, 1, 1)
        plt.hist(pixelgroup_1, bins=255)
        plt.semilogy()
        plt.title('Histogram of Group 1')

        plt.subplot(2, 1, 2)
        plt.hist(pixelgroup_2, bins=255)
        plt.semilogy()
        plt.title('Histogram of Group 2')
        plt.xlabel(f'Metric is {round(metric,3)}')

        fig.tight_layout()
        plt.show()

    return metric


def create_mask():
    array = np.load('eval_signal_reference/original_ref.npy')
    img = Image.fromarray(array).convert('L')

    blur_img = img.filter(ImageFilter.BoxBlur(25))
    blur_array = np.array(blur_img, dtype=np.uint8)

    mask_array = np.zeros((1080, 1920), dtype=np.uint8)
    mask_array[(0 <= blur_array) & (blur_array < 25)] = 2
    mask_array[(225 < blur_array) & (blur_array <= 255)] = 1

    out_img = Image.fromarray(mask_array).convert('P')
    out_img.putpalette([0,0,0, 255,0,0, 0,0,255])
    out_img.show()
    #out_img.save('eval_signal_reference/mask.png')
    #np.save('eval_signal_reference/mask', mask_array)


if __name__ == '__main__':
    m = evaluate_signal(np.load('some_tests/raw_test_frame.npy'), True)
    print(m)