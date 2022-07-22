from subprocess import Popen
import time

Popen('sleep 5 && touch amk.amk', shell=True)

print('DONE')