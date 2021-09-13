"""
MicroPython PCF8574具有中斷功能的8位I2C I/O擴展器
https://github.com/mcauser/micropython-pcf8574

麻省理工學院執照
版權所有(c)2019 Mike Causer

特此授予獲得副本的任何人免費的許可軟件和相關文檔文件（以下簡稱“軟件”）的交
易在軟件中不受限制，包括但不限於權利使用，複製，修改，合併，發布，分發，再許
可和/或出售本軟件的副本，並允許本軟件所針對的人具備以下條件：以上版權聲明和此
許可聲明應包含在所有複製或實質性的軟件部分。

本軟件按“原樣”提供，沒有任何形式的明示或明示擔保。暗示(包括但不限於適銷性的
保證)，適用於特定目的和非侵權。 在任何情況下都不會作者或版權所有者對任何索賠
，損害或其他責任無論是由於合同，侵權或其他原因而引起的責任，與軟件或軟件的使用
或其他交易無關或與之有關軟件。

使用方法：

#啟用I2C
import machine, os, time
from machine import Pin
scl = Pin(13)
sda = Pin(12)
i2c = machine.I2C(1, scl = scl, sda = sda, freq=400000)
i2c.scan()
print('I2C掃描裝置位址：', i2c.scan())         # 十進制編碼(0~127)

#啟用pcf8574
import pcf8574
pcf = pcf8574.PCF8574(i2c, 37)       # 建立物件：指定啟動鍵盤位址(0x20)
pcf.port = 0b11111111                # 以byte為單位一次寫入pin0~7
bin(pcf.port)                        # 列印所有腳位值
pcf.pin(1, value = 0)                # 以bit為單位指定寫入pin1值，為0(value非0則為1)
bin(pcf.port)                        # 列印所有腳位值
pcf.toggle(1)                        # "撥動"某pin
bin(pcf.port)                        # 列印所有腳位值

#純練習測試
PULUPA = 0x0F                        # 定義變數0b00001111(也可以寫15)
PULUPB = 0xF0                        # 定義變數0b11110000(也可以寫240)
bin(bytes([PULUPA])[0])              # 列印輸入值(bytes函數可強迫值為 1 byte)
pcf.port = PULUPA
bin(pcf.port)                        # 列印所有腳位值


#啟用pcf8574_SWITCH，可指定某腳位的開關與延時
import pcf8574
buzzer_4 = pcf8574.PCF8574_SWITCH(i2c, 37, 4)  # 建立物件：給定通道及單腳位
led_5 = pcf8574.PCF8574_SWITCH(i2c, 37, 5)     # 建立物件：給定通道及單腳位
led_6 = pcf8574.PCF8574_SWITCH(i2c, 37, 6)     # 建立物件：給定通道及單腳位

buzzer_4.on(300)
led_5.on()
led_6.on(1000)                         # 通電一秒後再關電
led_5.off(500)                         # 關電500毫秒後再通電
led_5.off()                            # 恆關電
bin(led_5.port)                        # 查看各路狀態

buzzer_4.sw_toggle(300)                # 反向300毫秒

"""

# [Python教學]@property是什麼? 使用場景和用法介紹(https://www.maxlist.xyz/2019/12/25/python-property/)
# [Python教學] 物件導向-Class類的封裝/繼承/多型(https://www.maxlist.xyz/2019/12/12/python-oop/)

import time

class PCF8574:                                  # 創立物件(一般都用大寫)
    def __init__(self, i2c, address = 0x20):    # import 就會執行__init__，__表示私有物件，不可被外部呼叫執行
        self._i2c = i2c                         # 承接i2c
        self._address = address                 # 承接i2c位址
        self._port = bytearray(1)               # 先建立1個byte的數組(內容為NULL:'\x00')
        if i2c.scan().count(address) == 0:      # 若導入的位址通訊失敗，則顯示錯誤
            raise OSError('PCF8574 not found at I2C address {:#x}'.format(address))

    def _read(self):                            # 更新當前腳位值為 self._port
        self._i2c.readfrom_into(self._address, self._port)     # 從address讀入成為_port陣列

    def _write(self):                           # 將self._port值寫入設備address
        self._i2c.writeto(self._address, self._port)

    @property                                   # 將 class (類) 的方法轉換為 只能讀取的 屬性
    def port(self):
        self._read()                            # 更新當前腳位值為 self._port
        return self._port[0]                    # 返回讀取的值

    @port.setter
    def port(self, value):
        self._port[0] = value & 0xff            # 確保資料
        self._write()                           # 執行self._write()
        # [為何與0xff進行與運算](https://www.itread01.com/articles/1476025221.html)

    def validate_pin(self, pin):                # 驗證腳位輸入 pin valid range 0..7
        if not 0 <= pin <= 7:
            raise ValueError('Invalid pin {}. Use 0-7.'.format(pin))
        return pin

    def pin(self, pin, value = None):           # 讀取或寫入某pin腳
        pin = self.validate_pin(pin)            # 先驗證腳位輸入在範圍內
        self._read()                            # 更新當前腳位值為 self._port
        if value is None:                       # 沒有指定值value就是「讀取模式」
            return (self._port[0] >> pin) & 1   # 要讀第幾pin就位移幾次， & 1 會只保留最後一位(好強！)
        else:                                   # 有指定值value就是「寫入模式」(無論是0或1)
            if value:                           # 若value值非0
                self._port[0] |= (1 << (pin))   # 要寫第幾pin就位移幾次，做「或」運算，可寫入該位(好強！)
            else:                               # 若值value為 0
                self._port[0] &= ~(1 << (pin))  # 要寫第幾pin就位移幾次，做「且」運算，可寫入該位(這超強！)
            self._write()

    def toggle(self, pin):                      # 撥動某pin
        pin = self.validate_pin(pin)
        self._read()                            # 更新當前腳位值為 self._port
        self._port[0] ^= (1 << (pin))           # 用XOR解決(只有一個1才是1)，超強的解法！
        self._write()

class PCF8574_SWITCH(PCF8574):                               # 創立物件(一般都用大寫)
    def __init__(self, i2c, address = 0x20, pin = 0):        # import 就會執行__init__，__表示私有物件，不可被外部呼叫執行
        self._pin_control = pin                              # 承接pin
        if i2c.scan().count(address) == 0:                   # 若導入的位址通訊失敗，則顯示錯誤
            raise OSError('PCF8574 not found at I2C address {:#x}'.format(address))
        if not 0 <= pin <= 7:
            raise ValueError('Invalid pin {}. Use 0-7.'.format(pin))
        super().__init__(i2c, address)                       # 利用上層函式庫來創立物件

    def on(self, duration_ms = 0):                           # 某pin通電(或只暫時通電sleep_ms 毫秒)
        self.pin(self._pin_control, 0)
        if duration_ms > 0:
            time.sleep_ms(duration_ms)                       # 持續設定時間後再關閉
            self.pin(self._pin_control, 1)

    def off(self, duration_ms = 0):                          # 某pin關電(或只暫時關電sleep_ms 毫秒)
        self.pin(self._pin_control, 1)
        if duration_ms > 0:
            time.sleep_ms(duration_ms)                       # 持續設定時間後再打開
            self.pin(self._pin_control, 0)

    def sw_toggle(self, duration_ms = 0):                    # 撥動某pin關電(或只暫時關電sleep_ms 毫秒)
        self.toggle(self._pin_control)
        if duration_ms > 0:
            time.sleep_ms(duration_ms)                       # 持續設定時間後再關閉
            self.toggle(self._pin_control)
