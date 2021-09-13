# -*- coding: utf-8 -*-
# Python宣告原始檔字元編碼的方式，寫在原始檔頂行

"""
Created on Thu Dec 20 16:10:13 2018

@author: Film
"""
# [詳解python string型別 bytes型別 bytearray型別] (https://codertw.com/%E7%A8%8B%E5%BC%8F%E8%AA%9E%E8%A8%80/362015/)

# Original from William Henning
# http://www.mikronauts.com/raspberry-pi/raspberry-pi-4x4-keypad-i2c-MCP23017-howto/

#測試程式碼
"""
#啟用I2C
import machine, os, time
from machine import Pin
scl = Pin(13)
sda = Pin(12)
i2c = machine.I2C(1, scl = scl, sda = sda, freq=400000)
i2c.scan()


#啟用pcf8574鍵盤
import pcf8574_i2c_keypad16
keypad = pcf8574_i2c_keypad16.PCF8574_keypad(i2c, 38, mode = 0)  # 指定鍵盤I2C位址為0x20(32)，預設模式0是最左邊接pin7,模式1是最左邊接pin0(反向)
keypad.PCF8574_keypad_main()                              # 執行測試程式


keypad.PCF8574_keypad_getch()                             # 抓一次鍵

"""

class PCF8574_keypad:                            # 創立物件(一般都用大寫)
    def __init__(self, i2c, address = 0x20, mode = 0):     # import 就會執行__init__，__表示私有物件，不可被外部呼叫執行，預設模式為0
        self._i2c = i2c                          # 承接i2c
        self._address = address                  # 承接i2c位址
        self._mode = mode                        # 模式：預設模式0是最左邊接pin7,模式1是最左邊接pin0(反向)
        self.PULUPA = 0x0F                       # 拉高A組(Pin 0~3)腳位為高電位
        self.PULUPB = 0xF0                       # 拉高B組(Pin 4~7)腳位為高電位
        if i2c.scan().count(address) == 0:       # 若導入的位址通訊失敗，則顯示錯誤
            raise OSError('PCF8574 not found at I2C address {:#x}'.format(address))

        # pin 的順序意義：76543210 代表C4、C3、C2、C1、R4、R3、R2、R1

        # Keypad 矩陣
        self.KEYCODE  = [['1','2','3','A'],              # KEYROW0
                         ['4','5','6','B'],              # KEYROW1
                         ['7','8','9','C'],              # KEYROW2
                         ['*','0','#','D']]              # KEYROW3

        # 定義解碼行列號(7,11,13,14)
        if self._mode == 0:
            self.DECODE = [-1,-1,-1,-1,-1,-1,-1, 0,-1,-1,-1, 1,-1, 2, 3,-1]       # 同時按下兩個按鍵以上返回-1
        else:
            self.DECODE = [-1,-1,-1,-1,-1,-1,-1, 3,-1,-1,-1, 2,-1, 1, 0,-1]       # 同時按下兩個按鍵以上返回-1

    def PCF8574_keypad_getch(self, until_second = -1):                            # 獲取一個按鍵值(預設無限等待)
        import time
        start_time = time.time()
        while (until_second < 0) or (time.time() - start_time < until_second):    # 若持續時間設定為負，或尚為達到停止時間，則繼續等待
            # time.sleep_ms(10)
            self._i2c.writeto(self._address, bytes([self.PULUPA]))                # 寫入 A組高電位
            row = self.DECODE[self._i2c.readfrom(self._address, 1)[0]]            # 讀取列號
            if (row) != -1:                                                       # 檢查 A組電位變化
                self._i2c.writeto(self._address, bytes([self.PULUPB]))            # 寫入 B組高電位
                col = self.DECODE[self._i2c.readfrom(self._address, 1)[0] >> 4]   # 讀取行號
                if (col) != -1:                                                   # 無論行列號解碼返回 -1 就是 非純按一鍵，忽略此次
                    if self._mode == 0:
                        return self.KEYCODE[col][row]                             # 只有按一個鍵，才返回按鍵值
                    else:
                        return self.KEYCODE[row][col]                             # 只有按一個鍵，才返回按鍵值
        return -1                                                                 # 未按下按鍵，返回 -1


    def PCF8574_keypad_main(self):                   # test code
        import time
        print('請按鍵盤按鈕(離開請按"#")：')
        while 1:
            ch = self.PCF8574_keypad_getch()         # 抓一鍵
            print(ch, end='')                        # 不斷行
            time.sleep_ms(300)                       # 控制讀取速度

            if ch == '#':                            # 結束此程式，離開迴圈
                print('')                            # 斷行
                break

    # don't runt test code if we are imported
    if __name__ == '__main__':
        main()
