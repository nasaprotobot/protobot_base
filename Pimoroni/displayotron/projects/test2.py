import time

import dothat.backlight as backlight
import dothat.lcd as lcd

lcd.clear()
lcd.write("Redy for combat!")

while True:
    for i in range(0,100):
        backlight.set_graph(i/100)
        
        backlight.sweep(i/1000 + .6, .01)
        time.sleep(.0025)
    
    for i in range(0,100):
        backlight.set_graph((100-i)/100)
        
        backlight.sweep((100-i)/1000 + .6, .01)
        time.sleep(.0025)