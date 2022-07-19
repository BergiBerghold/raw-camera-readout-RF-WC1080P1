from subprocess import Popen, PIPE, DEVNULL
import matplotlib.pyplot as plt
from threading import Thread, Lock
from collections import deque
import numpy as np
import time
import os


stop_flag = False
temperature_setpoint = None
temp_values = deque([], maxlen=100)


def set_psu(voltage, current):
    set_psu_cmd = ['ssh', 'experiment', 'KoradCLI', '/dev/ttyACM0', str(current), str(voltage)]

    if os.getenv('CCD_MACHINE'):
        set_psu_cmd = set_psu_cmd[2:]

    set_psu_process = Popen(set_psu_cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = set_psu_process.communicate()


def read_temperature_threaded(stop):
    global temp_values

    get_temp_cmd = ['ssh', '-tt', 'experiment', 'TempReadout']
    shell = False

    if os.getenv('CCD_MACHINE'):
        get_temp_cmd = get_temp_cmd[3:]
        shell = True

    with Popen(get_temp_cmd, stdout=PIPE, stderr=DEVNULL, bufsize=0, shell=shell) as p:
        for line in p.stdout:
            line = eval(line)

            ch1_temp = float(line[0][1])
            ch1_internal = float(line[0][0])

            temp_values.append({'probe': ch1_temp, 'internal': ch1_internal, 'timestamp': time.time()})
            print(f'{ch1_temp} °C')

            if stop():
                print('Killing')
                p.kill()
                break


def temperature_control_threaded(stop):
    global temp_values
    global temperature_setpoint

    psu_on = False

    while not stop():
        if temp_values and temperature_setpoint:
            if temp_values[-1]['probe'] < temperature_setpoint and time.time() - temp_values[-1]['timestamp'] < 10:
                if not psu_on:
                    set_psu(voltage=18, current=0.1)
                    psu_on = True
                    print('Tuning on PSU...')

            elif psu_on:
                set_psu(voltage=0, current=0.1)
                psu_on = False
                print('Tuning off PSU...')

            time.sleep(0.05)

    set_psu(voltage=0, current=0.1)
    print('Tuning off PSU...')


def set_temperature(temp):
    global temperature_setpoint
    temperature_setpoint = temp


def read_temperature():
    global temp_values
    return list(temp_values)


temp_readout_thread = Thread(target=read_temperature_threaded, args=(lambda: stop_flag, ))
temp_readout_thread.start()

temp_control_thread = Thread(target=temperature_control_threaded, args=(lambda: stop_flag, ))
temp_control_thread.start()


if __name__ == '__main__':
    stop_flag = False

    temp_readout_thread = Thread(target=read_temperature_threaded, args=(lambda: stop_flag,))
    temp_readout_thread.start()

    temp_control_thread = Thread(target=temperature_control_threaded, args=(20, lambda: stop_flag))
    temp_control_thread.start()

    input("STOP?")

    stop_flag = True
    temp_readout_thread.join()
    temp_control_thread.join()

