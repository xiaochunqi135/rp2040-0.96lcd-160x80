from ST7735 import TFT
from sysfont import sysfont
from machine import SPI,Pin
import time
import math

LCD_DC = 8
LCD_CS = 9
LCD_CLK = 10
LCD_DIN = 11
LCD_RST = 12
LCD_BL = 25

spi = SPI(1, baudrate=10_000_000, polarity=0, phase=0, sck=Pin(LCD_CLK), mosi=Pin(LCD_DIN), miso=None)
tft=TFT(spi,LCD_DC,LCD_RST,LCD_CS)
tft.init_backlight(LCD_BL)

tft.backlight(20)

def testlines(color):
    tft.fill(TFT.BLACK)
    for x in range(0, tft.size()[0], 6):
        tft.line((0,0),(x, tft.size()[1] - 1), color)
    for y in range(0, tft.size()[1], 6):
        tft.line((0,0),(tft.size()[0] - 1, y), color)
    tft.fill(TFT.BLACK)
    for x in range(0, tft.size()[0], 6):
        tft.line((tft.size()[0] - 1, 0), (x, tft.size()[1] - 1), color)
    for y in range(0, tft.size()[1], 6):
        tft.line((tft.size()[0] - 1, 0), (0, y), color)
    tft.fill(TFT.BLACK)
    for x in range(0, tft.size()[0], 6):
        tft.line((0, tft.size()[1] - 1), (x, 0), color)
    for y in range(0, tft.size()[1], 6):
        tft.line((0, tft.size()[1] - 1), (tft.size()[0] - 1,y), color)
    tft.fill(TFT.BLACK)
    for x in range(0, tft.size()[0], 6):
        tft.line((tft.size()[0] - 1, tft.size()[1] - 1), (x, 0), color)
    for y in range(0, tft.size()[1], 6):
        tft.line((tft.size()[0] - 1, tft.size()[1] - 1), (0, y), color)
    time.sleep(1)

def testfastlines(color1, color2):
    tft.fill(TFT.BLACK)
    for y in range(0, tft.size()[1], 5):
        tft.hline((0,y), tft.size()[0], color1)
    for x in range(0, tft.size()[0], 5):
        tft.vline((x,0), tft.size()[1], color2)
    time.sleep(3)

def testdrawrects(color):
    tft.fill(TFT.BLACK)
    for x in range(0,tft.size()[0],6):
        tft.rect((tft.size()[0]//2 - x//2, tft.size()[1]//2 - x/2), (x, x), color)
    time.sleep(3)

def testfillrects(color1, color2):
    tft.fill(TFT.BLACK)
    for x in range(tft.size()[0],0,-6):
        tft.fillrect((tft.size()[0]//2 - x//2, tft.size()[1]//2 - x/2), (x, x), color1)
        tft.rect((tft.size()[0]//2 - x//2, tft.size()[1]//2 - x/2), (x, x), color2)
    time.sleep(3)

def testfillcircles(radius, color):
    tft.fill(TFT.BLACK)
    for x in range(radius, tft.size()[0], radius * 2):
        for y in range(radius, tft.size()[1], radius * 2):
            tft.fillcircle((x, y), radius, color)
    time.sleep(1)

def testdrawcircles(radius, color):
    for x in range(0, tft.size()[0] + radius, radius * 2):
        for y in range(0, tft.size()[1] + radius, radius * 2):
            tft.circle((x, y), radius, color)
    time.sleep(1)

def testtriangles():
    tft.fill(TFT.BLACK)
    color = 0xF800
    w = tft.size()[0] // 2
    x = tft.size()[1] - 1
    y = 0
    z = tft.size()[0]
    for t in range(0, 15):
        tft.line((w, y), (y, x), color)
        tft.line((y, x), (z, x), color)
        tft.line((z, x), (w, y), color)
        x -= 4
        y += 4
        z -= 4
        color += 100
    time.sleep(1)

def testroundrects():
    tft.fill(TFT.BLACK)
    color = 100
    for t in range(5):
        x = 0
        y = 0
        w = tft.size()[0] - 2
        h = tft.size()[1] - 2
        for i in range(17):
            tft.rect((x, y), (w, h), color)
            x += 2
            y += 3
            w -= 4
            h -= 6
            color += 1100
        color += 100
    time.sleep(1)

def tftprinttest():
    tft.fill(TFT.BLACK)
    v = 0
    tft.text((0, v), "Hello 0!", TFT.RED, sysfont, 1, nowrap=True)
    v += sysfont["Height"]
    tft.text((0, v), "Hello 1!", TFT.YELLOW, sysfont, 2, nowrap=True)
    v += sysfont["Height"] * 2
    tft.text((0, v), "Hello 2!", TFT.GREEN, sysfont, 3, nowrap=True)
    v += sysfont["Height"] * 3
    tft.text((0, v), str(123.567), TFT.BLUE, sysfont, 4, nowrap=True)
    time.sleep(5)
    tft.fill(TFT.BLACK)
    v = 0
    tft.text((0, v), "Hello Pico!", TFT.RED, sysfont)
    v += sysfont["Height"]
    tft.text((0, v), str(math.pi), TFT.GREEN, sysfont)
    v += sysfont["Height"]
    tft.text((0, v), " This is pi", TFT.GREEN, sysfont)
    v += sysfont["Height"] * 2
    tft.text((0, v), hex(8675309), TFT.GREEN, sysfont)
    v += sysfont["Height"]
    tft.text((0, v), " Print HEX 8675309", TFT.GREEN, sysfont)
    v += sysfont["Height"] * 2
    tft.text((0, v), "Sketch has been", TFT.WHITE, sysfont)
    v += sysfont["Height"]
    tft.text((0, v), "running for: ", TFT.WHITE, sysfont)
    v += sysfont["Height"]
    tft.text((0, v), str(time.ticks_ms() / 1000), TFT.PURPLE, sysfont)
    tft.text((45, v), " seconds.", TFT.WHITE, sysfont)
    time.sleep(5)

def testRotation():
    i = tft.rotate
    for x in range (0, 4) :
        tft.rotation(i)
        tft.fill(TFT.BLACK)
        tft.rect((0,0),tft.size(), TFT.WHITE)
        tft.rect((2,2),(tft.size()[0]-4, tft.size()[1]-4), TFT.YELLOW)
        tft.rect((4,4),(tft.size()[0]-8, tft.size()[1]-8), TFT.RED)
        tft.fillrect((0,0),(8,8),TFT.GREEN)
        tft.text((20, 20), "TEST", TFT.RED, sysfont, 2)
        time.sleep_ms(3000)
        i = i + 1 if i < 3 else 0
    tft.fill(TFT.BLACK)
    tft.rotation(i)
    time.sleep(3)

while True:
    testlines(TFT.RED)
    testfastlines(TFT.RED, TFT.BLUE)
    testdrawrects(TFT.GREEN)
    testfillrects(TFT.YELLOW, TFT.PURPLE)
    testfillcircles(10, TFT.BLUE)
    testdrawcircles(10, TFT.WHITE)
    testtriangles()
    testroundrects()
    tftprinttest()
    testRotation()