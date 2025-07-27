import thermohygrometer
import day_neopixel
import datetime

dt = datetime.datetime.now()


thermohygrometer.main()
day_neopixel.main(dt.hour)