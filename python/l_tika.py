from gpiozero import LED
from time import sleep,time

led = LED(17)
timeStart = time()

while True:
    led.on()
    sleep(1)
    led.off()
    sleep(1)
    print('time:{0:.3f}'.format( time() - timeStart))