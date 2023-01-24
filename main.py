from ST7735 import TFT,TFTColor
from sysfont import sysfont
from machine import SPI,Pin,ADC
import time
import math

LCD_DC = 8
LCD_CS = 9
LCD_CLK = 10
LCD_DIN = 11
LCD_RST = 12
LCD_BL = 25

class temp_sensor():
    def __init__(self):
        self.sensor = ADC(4)
        self.temperature = 0
        self.ftext = "00.00"
    def update(self):
        sensor_voltage = self.sensor.read_u16() * 3.3 / 65535
        self.temperature = 27 - (sensor_voltage - 0.706) / 0.001721
        self.ftext = "{0:.2f}".format(self.temperature)

spi = SPI(1, baudrate=10_000_000, polarity=0, phase=0, sck=Pin(LCD_CLK), mosi=Pin(LCD_DIN), miso=None)
lcd=TFT(spi,LCD_DC,LCD_RST,LCD_CS)
lcd.init_backlight(LCD_BL)
lcd.backlight(100)

# tft.rotation(0)
# tft.background('vbg.bmp')

tmps = temp_sensor()

lcd.fill(lcd.BLACK)
lcd.text((20,30), "Hello pico!", lcd.RED, sysfont, 2, nowrap=True)
time.sleep(5)

lcd.backlight(10)
lcd.background('bg.bmp')
j,k = 60,28
while True:
    tmps.update()
    lcd.fillrect((j,k), (60, 16), TFT.WHITE)
    lcd.text((j,k), tmps.ftext, TFT.RED, sysfont,2)
    time.sleep(3)
    tmps.update()
    lcd.fillrect((j,k), (60, 16), TFT.WHITE)
    lcd.text((j,k), tmps.ftext, TFT.GREEN, sysfont,2)
    time.sleep(3)
    tmps.update()
    lcd.fillrect((j,k), (60, 16), TFT.WHITE)
    lcd.text((j,k), tmps.ftext, TFT.BLUE, sysfont,2)
    time.sleep(3)
    tmps.update()
    lcd.fillrect((j,k), (60, 16), TFT.WHITE)
    lcd.text((j,k), tmps.ftext, TFT.BLACK, sysfont,2)
    time.sleep(3)