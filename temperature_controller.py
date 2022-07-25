from subprocess import Popen, PIPE, DEVNULL
from collections import deque
from threading import Thread
from simple_pid import PID
import curses
import time
import os


stop_flag = False
psu_voltage = None
temp_values = deque([], maxlen=100)


def set_psu(voltage, current):
    global psu_voltage
    psu_voltage = voltage

    set_psu_cmd = ['ssh',
                   'experiment',
                   'KoradCLI',
                   '/dev/serial/by-id/usb-Nuvoton_USB_Virtual_COM_000913960243-if00',
                   str(current),
                   str(voltage)]

    if os.getenv('CCD_MACHINE'):
        set_psu_cmd = set_psu_cmd[2:]

    set_psu_process = Popen(set_psu_cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = set_psu_process.communicate()


def read_temperature_threaded(stop):
    global temp_values

    get_temp_cmd = ['ssh', 'experiment', 'TempReadout', '1']

    if os.getenv('CCD_MACHINE'):
        get_temp_cmd = get_temp_cmd[2:]

    while not stop():
        get_temp_process = Popen(get_temp_cmd, stdout=PIPE, stderr=DEVNULL)
        stdout, _ = get_temp_process.communicate()

        try:
            line = eval(stdout)

            ch1_temp = float(line[0][1])
            ch1_internal = float(line[0][0])

            if ch1_temp > 100:
                ch1_temp -= 4096

            if ch1_internal > 100:
                ch1_internal -= 256

            temp_values.append({'probe': ch1_temp, 'internal': ch1_internal, 'timestamp': time.time()})

            with open('temp_log.txt', 'a') as f:
                f.writelines(str({'probe': ch1_temp, 'internal': ch1_internal, 'timestamp': time.time()}) + '\n')

        except:
            pass


def temperature_control_threaded(temperature_setpoint, stop):
    global temp_values

    psu_on = False
    pid = PID(1, 0.08, 0.35, setpoint=temperature_setpoint, output_limits=(0, 24))

    open('temp_setpoint.txt', 'w').close()

    while not stop():
        if temp_values:
            if time.time() - temp_values[-1]['timestamp'] < 10:
                current_temp = temp_values[-1]['probe']

                voltage = pid(current_temp)

                set_psu(voltage=voltage, current=0.1)

            else:
                set_psu(voltage=0, current=0.1)

        try:
            with open('temp_setpoint.txt', 'r') as f:
                pid.setpoint = float(f.readline())

        except:
            pass

    set_psu(voltage=0, current=0.1)


if __name__ == '__main__':
    print('\nLaunching Temperature Controller\n')

    try:
        temperature_setpoint = float(input('Enter temp. Setpoint: '))
    except:
        print('Conversion to float failed. Exiting...')
        exit()

    stop_flag = False

    temp_readout_thread = Thread(target=read_temperature_threaded, args=(lambda: stop_flag, ))
    temp_readout_thread.start()

    temp_control_thread = Thread(target=temperature_control_threaded, args=(temperature_setpoint, lambda: stop_flag))
    temp_control_thread.start()

    while not temp_values:
        time.sleep(0.01)

    stdscr = curses.initscr()
    curses.start_color()
    curses.use_default_colors()

    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)

    try:
        while True:
            stdscr.addstr(0, 0, f'Temperature Control Active', curses.color_pair(11))

            stdscr.addstr(2, 0, f'Sensor Temp.    Internal Temp.    Setpoint    PSU Voltage    last update', curses.color_pair(12))
            stdscr.addstr(3, 0, f'{round(temp_values[-1]["probe"],2)} °C    ')
            stdscr.addstr(3, 16, f'{round(temp_values[-1]["internal"],2)} °C    ')
            stdscr.addstr(3, 34, f'{temperature_setpoint} °C    ')
            stdscr.addstr(3, 46, f'{round(psu_voltage, 2)} V    ')
            stdscr.addstr(3, 61, f'{round(time.time() - temp_values[-1]["timestamp"], 3)} s    ')

            stdscr.addstr(5, 0, f'')

            time.sleep(0.05)
            stdscr.refresh()

            try:
                with open('temp_setpoint.txt', 'r') as f:
                    temperature_setpoint = float(f.readline())

            except:
                pass

    except KeyboardInterrupt:
        curses.endwin()
        print('Stopping Temperature Controller...')

    stop_flag = True
    temp_readout_thread.join()
    print('Temp Readout Thread joined')
    temp_control_thread.join()
    print('Temp Control Thread joined')

    os.remove('temp_log.txt')
    os.remove('temp_setpoint.txt')



