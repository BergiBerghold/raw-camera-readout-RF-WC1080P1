from subprocess import Popen, PIPE, DEVNULL
import os


get_temp_cmd = ['ssh', '-tt', 'experiment', 'TempReadout']
shell = False

if os.getenv('CCD_MACHINE'):
    get_temp_cmd = get_temp_cmd[3:]

with Popen(get_temp_cmd, stdout=PIPE, stderr=DEVNULL, bufsize=0) as p:
    for line in p.stdout:
        print(line)
        try:
            line = eval(line)

            ch1_temp = float(line[0][1])
            ch1_internal = float(line[0][0])