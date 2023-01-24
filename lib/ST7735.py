import machine
import time
from math import sqrt

TFTRotations=[0x00,0x60,0xC0,0xA0] # 0,90,180,270 degrees
TFTBGR=0x08

#@micropython.native
def clamp(aValue,aMin,aMax):
    return max(aMin,min(aMax,aValue))

#@micropython.native
def TFTColor(aR,aG,aB):
    return((aR & 0xF8) << 8) |((aG & 0xFC) << 3) |(aB >> 3)

class TFT(object):
    NOP=0x0
    SWRESET=0x01
    RDDID=0x04
    RDDST=0x09
    SLPIN=0x10
    SLPOUT=0x11
    PTLON=0x12
    NORON=0x13
    INVOFF=0x20
    INVON=0x21
    DISPOFF=0x28
    DISPON=0x29
    CASET=0x2A
    RASET=0x2B
    RAMWR=0x2C
    RAMRD=0x2E
    COLMOD=0x3A
    MADCTL=0x36
    FRMCTR1=0xB1
    FRMCTR2=0xB2
    FRMCTR3=0xB3
    INVCTR=0xB4
    DISSET5=0xB6
    PWCTR1=0xC0
    PWCTR2=0xC1
    PWCTR3=0xC2
    PWCTR4=0xC3
    PWCTR5=0xC4
    VMCTR1=0xC5
    RDID1=0xDA
    RDID2=0xDB
    RDID3=0xDC
    RDID4=0xDD
    PWCTR6=0xFC
    GMCTRP1=0xE0
    GMCTRN1=0xE1

    BLACK=0
    RED=TFTColor(0xFF,0x00,0x00)
    MAROON=TFTColor(0x80,0x00,0x00)
    GREEN=TFTColor(0x00,0xFF,0x00)
    FOREST=TFTColor(0x00,0x80,0x80)
    BLUE=TFTColor(0x00,0x00,0xFF)
    NAVY=TFTColor(0x00,0x00,0x80)
    CYAN=TFTColor(0x00,0xFF,0xFF)
    YELLOW=TFTColor(0xFF,0xFF,0x00)
    PURPLE=TFTColor(0xFF,0x00,0xFF)
    WHITE=TFTColor(0xFF,0xFF,0xFF)
    GRAY=TFTColor(0x80,0x80,0x80)

    @staticmethod
    def color(aR,aG,aB):
        return TFTColor(aR,aG,aB)

    def __init__(self,spi,aDC,aReset,aCS):
        self.rotate=2
        self.dc=machine.Pin(aDC,machine.Pin.OUT)
        self.reset=machine.Pin(aReset,machine.Pin.OUT)
        self.cs=machine.Pin(aCS,machine.Pin.OUT)
        self.cs(1)
        self.spi=spi
        self.colorData=bytearray(2)
        self.windowLocData=bytearray(4)
        self._reset()
        self._writecommand(TFT.SWRESET)
        time.sleep_us(150)
        self._writecommand(TFT.SLPOUT)
        time.sleep_us(255)
        data3=bytearray([0x01,0x2C,0x2D])
        self._writecommand(TFT.FRMCTR1)
        self._writedata(data3)
        self._writecommand(TFT.FRMCTR2)
        self._writedata(data3)
        data6=bytearray([0x01,0x2c,0x2d,0x01,0x2c,0x2d])
        self._writecommand(TFT.FRMCTR3)
        self._writedata(data6)
        time.sleep_us(10)
        self._writecommand(TFT.INVCTR)
        self._writedata(bytearray([0x07]))
        self._writecommand(TFT.PWCTR1)
        data3[0]=0xA2
        data3[1]=0x02
        data3[2]=0x84
        self._writedata(data3)
        self._writecommand(TFT.PWCTR2)
        self._writedata(bytearray([0xC5]))
        data2=bytearray(2)
        self._writecommand(TFT.PWCTR3)
        data2[0]=0x0A
        data2[1]=0x00
        self._writedata(data2)
        self._writecommand(TFT.PWCTR4)
        data2[0]=0x8A
        data2[1]=0x2A
        self._writedata(data2)
        self._writecommand(TFT.PWCTR5)
        data2[0]=0x8A
        data2[1]=0xEE
        self._writedata(data2)
        self._writecommand(TFT.VMCTR1)
        self._writedata(bytearray([0x0E]))
        self._writecommand(TFT.INVOFF)
        self._size=(80,160)
        self._offset=(26,1)
        self._writecommand(TFT.INVON)
        self.rotation(1)
        self._setMADCTL()
        self._writecommand(TFT.COLMOD)
        self._writedata(bytearray([0x05]))
        self._writecommand(TFT.CASET)
        self.windowLocData[0]=0x00
        self.windowLocData[1]=self._offset[0]
        self.windowLocData[2]=0x00
        self.windowLocData[3]=self._size[0]+self._offset[0]
        self._writedata(self.windowLocData)
        self._writecommand(TFT.RASET)
        self.windowLocData[1]=self._offset[1]
        self.windowLocData[3]=self._size[1]+self._offset[1]
        self._writedata(self.windowLocData)
        dataGMCTRP=bytearray([0x02,0x1c,0x07,0x12,0x37,0x32,0x29,0x2d,0x29,0x25,0x2b,0x39,0x00,0x01,0x03,0x10])
        self._writecommand(TFT.GMCTRP1)
        self._writedata(dataGMCTRP)
        dataGMCTRN=bytearray([0x03,0x1d,0x07,0x06,0x2e,0x2c,0x29,0x2d,0x2e,0x2e,0x37,0x3f,0x00,0x00,0x02,0x10])
        self._writecommand(TFT.GMCTRN1)
        self._writedata(dataGMCTRN)
        self._writecommand(TFT.NORON)
        time.sleep_us(10)
        self._writecommand(TFT.DISPON)
        time.sleep_us(100)
        self.cs(1)

    def size(self):
        return self._size

    def offset(self):
        return self._offset

    #@micropython.native
    def on(self,aBool=True):
        self._writecommand(TFT.DISPON if aBool else TFT.DISPOFF)

    #@micropython.native
    def invertcolor(self,aBool):
        self._writecommand(TFT.INVON if aBool else TFT.INVOFF)

    #@micropython.native
    def rotation(self,aRot):
        if(0 <= aRot < 4):
            rotchange=self.rotate ^ aRot
            self.rotate=aRot
        if(rotchange & 1):
            self._size=(self._size[1],self._size[0])
            self._offset=(self._offset[1],self._offset[0])
        self._setMADCTL()

    #@micropython.native
    def pixel(self,aPos,aColor):
        if 0 <= aPos[0] < self._size[0] and 0 <= aPos[1] < self._size[1]:
            self._setwindowpoint(aPos)
            self._pushcolor(aColor)

    #@micropython.native
    def text(self,aPos,aString,aColor,aFont,aSize=1,nowrap=False):
        if aFont == None:
            return
        if(type(aSize) == int) or(type(aSize) == float):
            wh=(aSize,aSize)
        else:
            wh=aSize
        px,py=aPos
        width=wh[0] * aFont["Width"] + 1
        for c in aString:
            self.char((px,py),c,aColor,aFont,wh)
            px += width
            if px + width > self._size[0]:
                if nowrap:
                    break
                else:
                    py += aFont["Height"] * wh[1] + 1
                    px=aPos[0]

    #@micropython.native
    def char(self,aPos,aChar,aColor,aFont,aSizes):
        if aFont == None:
            return
        startchar=aFont['Start']
        endchar=aFont['End']
        ci=ord(aChar)
        if(startchar <= ci <= endchar):
            fontw=aFont['Width']
            fonth=aFont['Height']
            ci=(ci - startchar) * fontw
            charA=aFont["Data"][ci:ci + fontw]
            px=aPos[0]
            if aSizes[0] <= 1 and aSizes[1] <= 1:
                for c in charA:
                    py=aPos[1]
                    for r in range(fonth):
                        if c & 0x01:
                            self.pixel((px,py),aColor)
                        py += 1
                        c >>= 1
                    px += 1
            else:
                for c in charA:
                    py=aPos[1]
                    for r in range(fonth):
                        if c & 0x01:
                            self.fillrect((px,py),aSizes,aColor)
                        py += aSizes[1]
                        c >>= 1
                    px += aSizes[0]

    #@micropython.native
    def line(self,aStart,aEnd,aColor):
        if aStart[0] == aEnd[0]:
            pnt=aEnd if(aEnd[1] < aStart[1]) else aStart
            self.vline(pnt,abs(aEnd[1] - aStart[1]) + 1,aColor)
        elif aStart[1] == aEnd[1]:
            pnt=aEnd if aEnd[0] < aStart[0] else aStart
            self.hline(pnt,abs(aEnd[0] - aStart[0]) + 1,aColor)
        else:
            px,py=aStart
            ex,ey=aEnd
            dx=ex - px
            dy=ey - py
            inx=1 if dx > 0 else -1
            iny=1 if dy > 0 else -1
            dx=abs(dx)
            dy=abs(dy)
            if(dx >= dy):
                dy <<= 1
                e=dy - dx
                dx <<= 1
                while(px != ex):
                    self.pixel((px,py),aColor)
                    if(e >= 0):
                        py += iny
                        e -=dx
                    e += dy
                    px += inx
            else:
                dx <<= 1
                e=dx - dy
                dy <<= 1
                while(py != ey):
                    self.pixel((px,py),aColor)
                    if(e >= 0):
                        px += inx
                        e -=dy
                    e += dx
                    py += iny

    #@micropython.native
    def vline(self,aStart,aLen,aColor):
        start=(clamp(aStart[0],0,self._size[0]),clamp(aStart[1],0,self._size[1]))
        stop=(start[0],clamp(start[1] + aLen,0,self._size[1]))
        if(stop[1] < start[1]):
            start,stop=stop,start
        self._setwindowloc(start,stop)
        self._setColor(aColor)
        self._draw(aLen)

    #@micropython.native
    def hline(self,aStart,aLen,aColor):
        start=(clamp(aStart[0],0,self._size[0]),clamp(aStart[1],0,self._size[1]))
        stop=(clamp(start[0] + aLen,0,self._size[0]),start[1])
        if(stop[0] < start[0]):
            start,stop=stop,start
        self._setwindowloc(start,stop)
        self._setColor(aColor)
        self._draw(aLen)

    #@micropython.native
    def rect(self,aStart,aSize,aColor):
        self.hline(aStart,aSize[0],aColor)
        self.hline((aStart[0],aStart[1] + aSize[1] - 1),aSize[0],aColor)
        self.vline(aStart,aSize[1],aColor)
        self.vline((aStart[0] + aSize[0] - 1,aStart[1]),aSize[1],aColor)

    #@micropython.native
    def fillrect(self,aStart,aSize,aColor):
        start=(clamp(aStart[0],0,self._size[0]),clamp(aStart[1],0,self._size[1]))
        end=(clamp(start[0] + aSize[0] - 1,0,self._size[0]),clamp(start[1] + aSize[1] - 1,0,self._size[1]))
        if(end[0] < start[0]):
            tmp=end[0]
            end=(start[0],end[1])
            start=(tmp,start[1])
        if(end[1] < start[1]):
            tmp=end[1]
            end=(end[0],start[1])
            start=(start[0],tmp)
        self._setwindowloc(start,end)
        numPixels=(end[0] - start[0] + 1) *(end[1] - start[1] + 1)
        self._setColor(aColor)
        self._draw(numPixels)

    #@micropython.native
    def circle(self,aPos,aRadius,aColor):
        self.colorData[0]=aColor >> 8
        self.colorData[1]=aColor
        xend=int(0.7071 * aRadius) + 1
        rsq=aRadius * aRadius
        for x in range(xend):
            y=int(sqrt(rsq - x * x))
            xp=aPos[0] + x
            yp=aPos[1] + y
            xn=aPos[0] - x
            yn=aPos[1] - y
            xyp=aPos[0] + y
            yxp=aPos[1] + x
            xyn=aPos[0] - y
            yxn=aPos[1] - x
            self._setwindowpoint((xp,yp))
            self._writedata(self.colorData)
            self._setwindowpoint((xp,yn))
            self._writedata(self.colorData)
            self._setwindowpoint((xn,yp))
            self._writedata(self.colorData)
            self._setwindowpoint((xn,yn))
            self._writedata(self.colorData)
            self._setwindowpoint((xyp,yxp))
            self._writedata(self.colorData)
            self._setwindowpoint((xyp,yxn))
            self._writedata(self.colorData)
            self._setwindowpoint((xyn,yxp))
            self._writedata(self.colorData)
            self._setwindowpoint((xyn,yxn))
            self._writedata(self.colorData)

    #@micropython.native
    def fillcircle(self,aPos,aRadius,aColor):
        rsq=aRadius * aRadius
        for x in range(aRadius):
            y=int(sqrt(rsq - x * x))
            y0=aPos[1] - y
            ey=y0 + y * 2
            y0=clamp(y0,0,self._size[1])
            ln=abs(ey - y0) + 1

            self.vline((aPos[0] + x,y0),ln,aColor)
            self.vline((aPos[0] - x,y0),ln,aColor)

    #@micropython.native
    def fill(self,aColor=BLACK):
        self.fillrect((0,0),self._size,aColor)

    #@micropython.native
    def _setColor(self,aColor):
        self.colorData[0]=aColor >> 8
        self.colorData[1]=aColor
        self.buf=bytes(self.colorData) * 32

    #@micropython.native
    def _draw(self,aPixels):
        self.dc(1)
        self.cs(0)
        for i in range(aPixels // 32):
            self.spi.write(self.buf)
        rest=(int(aPixels) % 32)
        if rest > 0:
            buf2=bytes(self.colorData) * rest
            self.spi.write(buf2)
        self.cs(1)

    #@micropython.native
    def _setwindowpoint(self,aPos):
        x=self._offset[0] + int(aPos[0])
        y=self._offset[1] + int(aPos[1])
        self._writecommand(TFT.CASET)
        self.windowLocData[0]=self._offset[0]
        self.windowLocData[1]=x
        self.windowLocData[2]=self._offset[0]
        self.windowLocData[3]=x
        self._writedata(self.windowLocData)
        self._writecommand(TFT.RASET)
        self.windowLocData[0]=self._offset[1]
        self.windowLocData[1]=y
        self.windowLocData[2]=self._offset[1]
        self.windowLocData[3]=y
        self._writedata(self.windowLocData)
        self._writecommand(TFT.RAMWR)

    #@micropython.native
    def _setwindowloc(self,aPos0,aPos1):
        self._writecommand(TFT.CASET)
        self.windowLocData[0]=self._offset[0]
        self.windowLocData[1]=self._offset[0] + int(aPos0[0])
        self.windowLocData[2]=self._offset[0]
        self.windowLocData[3]=self._offset[0] + int(aPos1[0])
        self._writedata(self.windowLocData)
        self._writecommand(TFT.RASET)
        self.windowLocData[0]=self._offset[1]
        self.windowLocData[1]=self._offset[1] + int(aPos0[1])
        self.windowLocData[2]=self._offset[1]
        self.windowLocData[3]=self._offset[1] + int(aPos1[1])
        self._writedata(self.windowLocData)
        self._writecommand(TFT.RAMWR)

    #@micropython.native
    def _writecommand(self,aCommand):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([aCommand]))
        self.cs(1)

    #@micropython.native
    def _writedata(self,aData):
        self.dc(1)
        self.cs(0)
        self.spi.write(aData)
        self.cs(1)

    #@micropython.native
    def _pushcolor(self,aColor):
        self.colorData[0]=aColor >> 8
        self.colorData[1]=aColor
        self._writedata(self.colorData)

    #@micropython.native
    def _setMADCTL(self):
        self._writecommand(TFT.MADCTL)
        rgb=TFTBGR
        self._writedata(bytearray([TFTRotations[self.rotate] | rgb]))

    #@micropython.native
    def _reset(self):
        self.dc(0)
        self.reset(1)
        time.sleep_us(500)
        self.reset(0)
        time.sleep_us(500)
        self.reset(1)
        time.sleep_us(500)
    
    def backlight(self, value):
        if value >= 100:
            value = 100
        self.bl.duty_u16(int(value * 65536 / 100))

    def init_backlight(self, aBL):
        self.bl = machine.PWM(machine.Pin(aBL))
        self.bl.freq(1000)

    def background(self, aFile):
        f=open(aFile, 'rb')
        if f.read(2) == b'BM': #check bitmap signature
            dummy = f.read(8)
            offset = int.from_bytes(f.read(4), 'little')
            hdrsize = int.from_bytes(f.read(4), 'little')
            width = int.from_bytes(f.read(4), 'little')
            height = int.from_bytes(f.read(4), 'little')
            if int.from_bytes(f.read(2), 'little') == 1:
                depth = int.from_bytes(f.read(2), 'little')
                if depth == 24 and int.from_bytes(f.read(4), 'little') == 0:
                    rowsize = (width * 3 + 3) & ~3
                    if height < 0:
                        height = -height
                        flip = False
                    else:
                        flip = True
                    if self.rotate == 1 or self.rotate == 3:
                        w,h = 160,80
                    else:
                        w,h = 80,160
                    self._setwindowloc((0,0),(w - 1,h - 1))
                    for row in range(h):
                        if flip:
                            pos = offset + (height - 1 - row) * rowsize
                        else:
                            pos = offset + row * rowsize
                        if f.tell() != pos:
                            dummy = f.seek(pos)
                        for col in range(w):
                            bgr = f.read(3)
                            self._pushcolor(TFTColor(bgr[2],bgr[1],bgr[0]))