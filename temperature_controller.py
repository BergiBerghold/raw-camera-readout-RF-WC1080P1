import time
from subprocess import Popen, PIPE, DEVNULL
from threading import Thread, Lock
import os


temp_values = []


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

    with Popen(get_temp_cmd, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            line = eval(line)

            ch1_temp = float(line[0][1])
            ch1_internal = float(line[0][0])

            #lock.acquire()
            #temp_values.append((ch1_internal, ch1_temp))
            print(ch1_temp)
            #lock.release()

            if stop():
                print('Killing')
                p.kill()
                break


def main():
    lock = Lock()
    stop_flag = False

    t1 = Thread(target=read_temperature, args=(lambda: stop_flag, ))

    t1.start()

    input("STOP?")

    stop_flag = True
    t1.join()



if __name__ == '__main__':
    main()