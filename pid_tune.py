import matplotlib.pyplot as plt
from collections import deque

temps_array = deque([], maxlen=300)
old_timestamp = None

plt.ion()

while True:
    with open('temp_log.txt', 'r') as f:
        temp_dict = eval(f.readlines()[-1])
        temp_value = float(temp_dict['probe'])

        if old_timestamp != temp_dict['timestamp']:
            temps_array.append(temp_value)
            old_timestamp = temp_dict['timestamp']

    try:
        with open('temp_setpoint.txt', 'r') as f:
            temperature_setpoint = float(f.readline())

        plt.axhline(y=temperature_setpoint, color='r', linestyle='-')

    except:
        pass


    plt.plot(list(temps_array))
    plt.draw()
    plt.pause(0.0001)
    plt.clf()
