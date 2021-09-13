'''
# 啟用I2C
from machine import I2C, Pin
import os, time
i2c = I2C(1, scl = Pin(13), sda = Pin(12), freq = 400000)
print('I2C掃描裝置位址：', i2c.scan())

# 啟用OLED
import ssd1306_tools, ssd1306_symbol, ssh1106
oled = ssd1306_tools.SSD1306_I2C(128, 64, i2c, addr = 0x3c)   # 建立物件，0.96寸設定的寬高像素
#oled = ssd1306_tools.SH1106_I2C(128, 64, i2c, None, 60)    #1.3吋改這列(None=SPI用Res腳，60=addr)


str = 'Welcome'
oled.show_text12_Line(str, line = 0, x = 0, inverse = False, animation = 1, show = 1, overlap = False)   # 單列顯示文字(共四列)，顯示前會先自動清除該列
oled.show_pic_in_main(_fmbuf = ssd1306_symbol.W128H48()._MCVS_ENGINEER, w = 128, h = 48, inverse = False, show = 1)    # 顯示開始畫面(攻城獅)

time.sleep_ms(1000)
oled.clear_H16_Line(line = 0, x = 0, c = 0, fill = 1, show = 1)                         # 單列刪除，c外框、fill填滿
time.sleep_ms(300)
oled.clear_main(c = 0, fill = 1, show = 1)    # 清除主顯示區域

oled.show_text12_Line('123456789012', line = 1, x = 0, inverse = False, animation = 1, show = 1, overlap = False)   # 單列顯示文字(共四列)
oled.show_text12('abcd', x = 64, y = 32, inverse = False, animation = 1, show = 1)      # 指定文字顯示的位置(可疊加)
time.sleep_ms(1000)
oled.clear()         # 清除全螢幕內容

# -----/////////即將刪除--動畫圓//////////-----
oled.show_animation_circle(x = 64, y = 42, r = 10, c = 1, fill = 0, show = 1)
oled.show_animation_ellipse(x = 64, y = 42, a = 10, b = 5, c = 1, fill = 0, show = 1)



'''

import ssd1306, framebuf, math, time, sh1106

import ssd1306_symbol                         # 引入圖片及字型檔
text12 = ssd1306_symbol.W12H16()              # 建立各字型物件
symbol16 = ssd1306_symbol.W16H16()
symbol24 = ssd1306_symbol.W24H24()
symbol32 = ssd1306_symbol.W32H32()
symbol48 = ssd1306_symbol.W48H48()
pic_128_48 = ssd1306_symbol.W128H48()         # 圖片檔


# 從原本的 SSD1306_I2C 繼承全部方法，改寫為增強型
class SSD1306_TOOLS():
# 顯示文字
    def show_text(self, str, x = 0, y = 0, show = 0):
        self.text(str, x, y)     # 顯示文字、左上角座標

        if show == 1:            # 立即更新畫面
            self.show()

# 12號英文字顯示函數(12x16)
    def show_text12(self, str, x = 0, y = 0, inverse = False, animation = 1, show = 1):
        for i in str:
            self.show_rect(x, y, 12, 16, c = 0, fill = 1, show = animation)    # 先清除將要填入的範圍。animation：逐字更新
            time.sleep_ms(5)
            self.show_pic(text12._BIGNUM[i], x, y, 12, 16, inverse, 0)  # 取得文字圖形檔，繪製文字
            x += 12

        if (animation | show) == 1:            # 立即更新畫面
            self.show()

# 12號英文字逐列顯示函數(12x16)
    def show_text12_Line(self, str, line = 0, x = 0, inverse = False, animation = 1, show = 1, overlap = False):
        if line > 4:
            line = 4
        elif line < 0:
            line = 0

        if x != 0:              # 若有指定x值，一律使用疊加模式
            overlap = True

        if overlap == False:
            self.clear_H16_Line(line = line, c = 0, fill = 1, show = 1)        # 預設先清除顯示列，否則可疊加

        y = 16 * line
        for i in str:
            self.show_rect(x, y, 12, 16, c = 0, fill = 1, show = animation)    # 先清除將要填入的範圍。animation：逐字更新
            time.sleep_ms(5)
            self.show_pic(text12._BIGNUM[i], x, y, 12, 16, inverse, 0)         # 取得文字圖形檔，繪製文字
            x += 12

        if (animation | show) == 1:            # 立即更新畫面
            self.show()


# 16號中文字顯示函數(16x16)
    def show_text16(self, str, x = 0, y = 0, inverse = False, animation = 1, show = 1):
        for i in str:
            self.show_rect(x, y, 16, 16, c = 0, fill = 1, show = animation)    # animation：逐字更新
            time.sleep_ms(5)
            self.show_pic(symbol16._BIGNUM[i], x, y, 16, 16, inverse, 0)  # 取得文字圖形檔，繪製文字
            x += 16

        if (animation | show) == 1:            # 立即更新畫面
            self.show()

# ----------------------
# 圖片顯示(可反色化)
    def show_pic(self, _fmbuf = bytearray([]), x = 0, y = 0, w = 0, h = 0, inverse = False, show = 1):
        # 檢查輸入
        if type(_fmbuf) != bytearray:
            print('The type of input must be \'Bytearray\'')
            return
        elif (x < 0 |y < 0 |w <= 0 | h <= 0):
            print('Pic\'s (x,y) and weight and height must great than 0')

        if inverse == True:                        # 判斷是否取反
            _temp = bytearray([])
            for i in range(len(_fmbuf)):
                _temp.append(_fmbuf[i] ^ 0xFF)     # 數據取反
        else:
            _temp = _fmbuf                         # 數據直接使用

        _fb = framebuf.FrameBuffer(_temp, w, h, framebuf.MVLSB)   #先利用數據建立矩形區域
        self.blit(_fb, x, y)                                      #再填入左上角座標

        if show == 1:                              # 立即更新畫面
            self.show()


# 在主畫面中顯示圖片(可反色化)
    def show_pic_in_main(self, _fmbuf = bytearray([]), x = 0, y = 0, w = 128, h = 48, inverse = False, show = 1):
        y = y + 16
        self.show_pic(_fmbuf, x, y, w, h, inverse, show)

# ----------------------
# 畫線
    def show_line(self, x = 32, y = 16, x1 = 64, y1 = 64, c = 1, show = 1):     # 設定直線的起點座標、終點座標、顏色1=亮、立即更新畫面
        self.line(x, y, x1, y1, c)
        if show == 1:                              # 立即更新畫面
            self.show()

# 畫水平線
    def show_hline(self, x = 48, y = 16, w = 20, c = 1, show = 1):             # 設定直線的起點座標、長度、顏色1=亮、立即更新畫面
        self.hline(x, y, w, c)
        if show == 1:                              # 立即更新畫面
            self.show()

# 畫垂直線
    def show_vline(self, x = 48, y = 16, h = 20, c = 1, show = 1):             # 設定直線的起點座標、長度、顏色1=亮、立即更新畫面
        self.vline(x, y, h, c)
        if show == 1:                              # 立即更新畫面
            self.show()

# ----------------------
# 畫圓
    def show_circle(self, x = 64, y = 42, r = 10, c = 1, fill = 0, show = 1):              # 設定圓心座標、半徑、顏色1=亮、填滿1、立即更新畫面
        for i in range(0,360):
            ax = round(x + r * math.cos( math.radians(i) ) )
            ay = round(y + r * math.sin( math.radians(i) ) )
            if fill == 0:
                self.pixel(ax, ay, c)              # 畫空心圓
            else:
                self.line(x, y, ax, ay, c)         # 畫實心圓

        if show == 1:                              # 立即更新畫面
            self.show()

# ----------------------
# 畫動畫圓
    def show_animation_circle(self, x = 64, y = 42, r = 10, c = 1, fill = 0, show = 1):     # 設定圓心座標、半徑、顏色1=亮、填滿1、立即更新畫面
        last_x = -1
        last_y = -1
        for i in range(0,360):
            ax = round(x + r * math.cos( math.radians(i) ) )
            ay = round(y + r * math.sin( math.radians(i) ) )
            if i == 0:
                last_x = ax
                last_y = ay

            if last_x == ax and last_y == ay:
                continue

            if fill == 0:
                self.pixel(ax, ay, c)              # 畫空心圓
                self.show()                        # 立即更新畫面
            else:
                self.line(x, y, ax, ay, c)         # 畫實心圓
                self.show()                        # 立即更新畫面

# ----------------------
# 畫動畫橢圓
    def show_animation_ellipse(self, x = 64, y = 42, a = 10, b = 5, c = 1, fill = 0, show = 1):     # 設定圓心座標、半徑、顏色1=亮、填滿1、立即更新畫面
        for i in range(0,360):
            ax = round(x + a * math.cos( math.radians(i) ) )
            ay = round(y + b * math.sin( math.radians(i) ) )

            if fill == 0:
                self.pixel(ax, ay, c)              # 畫空心圓
                self.show()                        # 立即更新畫面
            else:
                self.line(x, y, ax, ay, c)         # 畫實心圓
                self.show()                        # 立即更新畫面



# ----------------------
# 畫矩形(預設主顯示區域框)
    def show_rect(self, x = 0, y = 16, w = 128, h = 48, c = 1, fill = 0, show = 1):      # 設定左上角座標、寬、高、顏色1=亮、填滿1、立即更新畫面
        if fill == 0:
            self.rect(x, y, w, h, c)               # 畫空心矩形
        else:
            self.fill_rect(x, y, w, h, c)          # 畫實心矩形

        if show == 1:                              # 立即更新畫面
            self.show()

# ----------------------
# 等價 畫矩形方法，清除全畫面，且立即執行
    def clear(self, x = 0, y = 0, w = 128, h = 64, c = 0, fill = 1, show = 1):
        try:
            self.show_rect(x, y, w, h, c, fill, show)    # 設定左上角座標、寬、高、顏色1=亮、填滿1、立即更新畫面
        except:                                          # 出了哪種錯誤，要有怎樣相對應的處理
            print('清除矩形區域 失敗')
        else:
            print('清除矩形區域 成功')

# ----------------------
# 等價 畫矩形方法，清除高度16的列，且立即執行
    def clear_H16_Line(self, line = 0, x = 0, c = 0, fill = 1, show = 1):
        if line > 4:
            line = 4
        elif line < 0:
            line = 0

        y = 16 * line
        try:
            self.show_rect(x, y, self.width, 16, c, fill, show)              # 設定左上角座標、寬、高、顏色1=亮、填滿1、立即更新畫面
        except:
            print('清除第{}列 失敗'.format(line))
        else:
            print('清除第{}列 成功'.format(line))

# ----------------------
# 等價 畫矩形方法，清除主顯示區域，且立即執行
    def clear_main(self, c = 0, fill = 1, show = 1):
        try:
            self.show_rect(0, 16, self.width, self.height, c, fill, show)    # 設定左上角座標、寬、高、顏色1=亮、填滿1、立即更新畫面
        except:
            print('清除矩形區域 失敗')
        else:
            print('清除矩形區域 成功')


#=======================================================================    

# 新的 SSD1306_I2C 類別(原生ssd1306.SSD1306_I2C引入後，再新增SSD1306_TOOLS方法群)
class SSD1306_I2C(SSD1306_TOOLS, ssd1306.SSD1306_I2C):
    def __init__(self, width, height, i2c, addr = 0x3C, external_vcc = False):
        self.width = width
        self.height = height
        super().__init__(width, height, i2c, addr, external_vcc)                   # 利用上層函式庫來創立物件


# 新的 SH1106_I2C 類別(原生sh1106.SH1106_I2C引入後，再新增SSD1306_TOOLS方法群)
class SH1106_I2C(SSD1306_TOOLS, sh1106.SH1106_I2C):
    def __init__(self, width, height, i2c, res = None, addr = 0x3C):
        self.width = width
        self.height = height
        super().__init__(width, height, i2c, res, addr)                   # 利用上層函式庫來創立物件



# 物件：主顯示區範圍(原生SSD1306_I2C引入後，再新增SSD1306_TOOLS方法群)
class SSD1306_I2C_SHOW_AREA():
    def __init__(self, oled, offset_x = 0, offset_y = 0, area_width = 128, area_height = 64):
        self._oled = oled                          # 引入已建立的全螢幕物件
        self._offset_x = offset_x                  # 建立主顯示區左上角x座標
        self._offset_y = offset_y                  # 建立主顯示區左上角y座標
        self._area_width = area_width              # 建立主顯示區寬
        self._area_height = area_height            # 建立主顯示區高

# 顯示文字
    def show_text(self, str, x = 0, y = 0, show = 0):
        self._oled.show_text(str, x + self._offset_x, y + self._offset_y, show)

# 12號字顯示函數(12x16)
    def show_text12(self, str, x = 0, y = 0, inverse = False, animation = 1, show = 0):
        self._oled.show_text12(str, x + self._offset_x, y + self._offset_y, inverse, animation, show)

# 顯示日期、時間
    def show_day_time(self, x = 0, y = 0, animation = 1, show = 1):
        self._oled.clear()                                                                                  # 清除物件的顯示區域
        strdate = '%02d/%02d' % (time.localtime()[1:3])                                                     # 取出月,日  %d用十進位顯示輸出
        strtime = '%02d:%02d' % (time.localtime()[3:5])                                                     # 取出時,分
        self._oled.show_text12(strdate, x + self._offset_x     , y + self._offset_y, True, animation, show)       # 顯示反色 月-日
        self._oled.show_text12(strtime, x + self._offset_x + 64, y + self._offset_y, False, animation, show)      # 顯示 時:分

# 圖片顯示(可反色化)
    def show_pic(self, _fmbuf = bytearray([]), x = 0, y = 0, w = -1, h = -1, inverse = False, show = 0):
        if w < 0 or h < 0:                    # 如果未輸入寬和高，設定為物件的最大寬和高
            w = self._area_width
            h = self._area_height
        self._oled.show_pic(_fmbuf, x + self._offset_x, y + self._offset_y, w, h, inverse, show)


# ----- 基本繪圖 -----
    def show_line(self, x = 32, y = 16, x1 = 64, y1 = 64, c = 1, show = 0):               # 畫兩點線：設定起點座標、終點座標
        self._oled.show_line( x + self._offset_x, y + self._offset_y, x1 + self._offset_x, y1 + self._offset_y, c, show)

    def show_hline(self, x = 48, y = 16, w = 20, c = 1, show = 0):                        # 畫水平線：設定起點座標、長度
        self._oled.hline(x + self._offset_x, y + self._offset_y, w, c)

    def show_vline(self, x = 48, y = 16, h = 20, c = 1, show = 0):                        # 畫垂直線：設定起點座標、長度
        self._oled.show_vline(x + self._offset_x, y + self._offset_y, h, c, show)

    def show_circle(self, x = 20, y = 20, r = 10, c = 1, fill = 0, show = 0):             # 畫圓：設定圓心座標、半徑
        self._oled.show_circle(x + self._offset_x, y + self._offset_y, r, c, fill, show)

    def show_rect(self, x = 0, y = 16, w = 64, h = 32, c = 1, fill = 0, show = 0):        # 畫矩形：設定左上角座標
        self._oled.show_rect(x + self._offset_x, y + self._offset_y, w, h, c, fill, show)

    def clear(self, x = 0, y = 0, w = -1, h = -1, c = 0, fill = 1, show = 1):             # 清除該物件顯示區域：顏色c
        if w < 0 or h < 0:                    # 如果未輸入寬和高，設定為物件的最大寬和高
            w = self._area_width
            h = self._area_height
        self._oled.clear(x + self._offset_x, y + self._offset_y, w, h, c, fill, show)


# 新的 SSD1306_SPI 類別
class SSD1306_SPI(SSD1306_TOOLS, ssd1306.SSD1306_SPI):
    def __init__(self, width, height, spi, dc, res, cs, external_vcc=False):
        super().__init__(width, height, i2c, addr=0x3C, external_vcc=False)    # 利用上層函式庫來創立物件
