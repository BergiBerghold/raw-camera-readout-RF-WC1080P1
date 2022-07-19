from subprocess import Popen, PIPE, DEVNULL
import matplotlib.pyplot as plt
from threading import Thread, Lock
from collections import deque
import time
import os


temp_values = deque(maxlen=100)


def set_psu(voltage, current):
    set_psu_cmd = ['ssh', 'experiment', 'KoradCLI', '/dev/ttyACM0', str(current), str(voltage)]

    if os.getenv('CCD_MACHINE'):
        set_psu_cmd = set_psu_cmd[2:]

    set_psu_process = Popen(set_psu_cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = set_psu_process.communicate()


def read_temperature(stop):
    global temp_values

    get_temp_cmd = ['ssh', 'experiment', 'TempReadout']

    if os.getenv('CCD_MACHINE'):
        get_temp_cmd = get_temp_cmd[2:]

    # plt.ion()
    #
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # line1, = ax.plot(list(range(len(temp_values))), temp_values)

    with Popen(get_temp_cmd, stdout=PIPE, bufsize=0) as p:
        for line in p.stdout:
            line = eval(line)

            ch1_temp = float(line[0][1])
            ch1_internal = float(line[0][0])

            temp_values.append((ch1_internal, ch1_temp))
            print(ch1_temp)

            if stop():
                print('Killing')
                p.kill()
                break


def main():
    stop_flag = False

    temp_readout_thread = Thread(target=read_temperature, args=(lambda: stop_flag, ))
    temp_readout_thread.start()

    input("STOP?")

    stop_flag = True
    temp_readout_thread.join()


if __name__ == '__main__':
    main()