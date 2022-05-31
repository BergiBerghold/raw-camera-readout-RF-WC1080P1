from subprocess import Popen, PIPE
import os


def set_led(intensity=0):
    cmd = ['ssh', 'experiment', 'ProtoPWM', str(intensity)]

    if os.getenv('CCD_MACHINE'):
        cmd = cmd[2:]

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()