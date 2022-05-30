from subprocess import Popen, PIPE


def set_led(intensity=0):
    cmd = ['ssh', 'experiment', 'ProtoPWM', str(intensity)]

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()