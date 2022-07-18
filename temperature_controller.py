import os

psu_set_cmd = ['ssh', 'experiment', 'KoradCLI', '/dev/ttyACM0', current, voltage]

if os.getenv('CCD_MACHINE'):
    v4l2_cmd = v4l2_cmd[2:]

os.system()