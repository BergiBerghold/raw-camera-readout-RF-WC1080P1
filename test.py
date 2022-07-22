from subprocess import Popen
import time

Popen(['sleep', '5', '&&', 'ProtoPWM', str(5)], shell=True)

print('DONE')