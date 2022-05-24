import sys
import matplotlib.pyplot as plt

histogram_file = f'/Volumes/Ubuntu/eclipse_workspace_ubuntu/webcamreadout/Support/Test1.txt'

with open(histogram_file) as f:
    for line, color in zip(f.readlines(), ['red', 'blue', 'green']):
        values = line.split('},{')[1][:-3].split(',')
        values = [int(x) for x in values]

        lower = 120
        upper = 180

        print(values[lower:upper])
        plt.semilogy(range(len(values))[lower:upper], values[lower:upper], color=color)

    plt.show()