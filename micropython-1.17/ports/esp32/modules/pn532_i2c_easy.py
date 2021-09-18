'''
#使用方法：
#啟用I2C
import machine, os, time
from machine import Pin
scl = Pin(13)
sda = Pin(12)
i2c = machine.I2C(1, scl = scl, sda = sda, freq=400000)
print('I2C =', i2c.scan())

# ========
#啟用pn532
import pn532_i2c_easy
pn532 = pn532_i2c_easy.PN532(i2c, 36)           # 建立物件：指定啟動鍵盤位址(0x20)

# =====建立蜂鳴器
# 啟用pcf8574_SWITCH，可指定某腳位的開關與延時
# 建立 LED燈 和 蜂鳴器 物件，長腳直接接上正電
import pcf8574, time
buzzer = pcf8574.PCF8574_SWITCH(i2c, 38, 4)     # 建立物件：給定通道及單腳位
led_5 = pcf8574.PCF8574_SWITCH(i2c, 38, 5)        # 建立物件：給定通道及單腳位
led_6 = pcf8574.PCF8574_SWITCH(i2c, 38, 6)        # 建立物件：給定通道及單腳位

# =====喚醒並讀取UID
pn532.WAKEUP()                       # 喚醒PN532
buzzer.on(300)                       # 蜂鳴器響一聲

# 模式mode:[8H10D]十進制、[8H]陣列、[6H]、[SOCA]、[SOYAL]，Endianness:大頭派或小頭派
pn532.get_UID_n_Times(mode = '8H10D', Endianness = 'Big', times = 10)      # 最多偵測times次卡片就離開
buzzer.on(300)                       # 蜂鳴器響一聲

# =====測試資料打成封包
test_DATA = '00 01 1a 2c'
aa = b'\x01' + pn532.direct_combine_DATA(test_DATA)  # 將資料打包成封包
pn532.byte2str_hex(pn532.receive_DATA(aa))           # 嘗試拆解剛才的封包
print('\ntest_DATA =', test_DATA)                    # 原本的測試資料列印出來比對
buzzer.on(300)                                       # 蜂鳴器響一聲

# =====自訂編碼轉換
pn532.str_hex2byte(test_DATA)        # 字串轉bytes
pn532.byte2str_hex(aa)               # bytes 轉成字串觀看

'''

from machine import Pin, I2C
import time, ustruct

CMD_WAKEUP = b'\x55\x55\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\x03\xfd\xd4\x14\x01\x17\x00'
CMD_SCAN_ONE_CARD = b'\x00\x00\xff\x04\xfc\xd4\x4a\x01\x00\xe1\x00'

CMD_GET_VERSION = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\x02\xFE\xD4\x02\x2A'


PN532_ACK = b'\x01\x00\x00\xFF\x00\xFF\x00'
PN532_FRAME_START = b'\x01\x00\x00\xFF'
print('PN532 library Loadind...OK')


class PN532:                                    # 創立物件(一般都用大寫)

    def __init__(self, i2c, address = 0x24):    # import 就會執行__init__，__表示私有物件，不可被外部呼叫執行
        self._i2c = i2c                         # 承接i2c
        self._address = address                 # 承接i2c位址
        self._bytearr = bytearray()             # 準備共用的byte陣列
        self._str_hex = ''                      # 準備共用的字串陣列

        if i2c.scan().count(address) == 0:      # 若導入的位址通訊失敗，則顯示錯誤
            raise OSError('PN532 not found at I2C address {:#x}'.format(address))


# ======== 取得卡號UID
# 連續偵測n次卡片的函數(偵測模式, 大頭派或小頭派)
    def get_UID_n_Times(self, mode = '8H10D', Endianness = 'Big', times = 10):  # 返回卡號模式mode:[8H10D]十進制、[8H]陣列
        for i in range(times):
            UID = self.get_UID(mode, Endianness)
            if UID != -1:
                return UID
        print('Time out! Please check!')
        return -1


    def get_UID(self, mode = '8H10D', Endianness = 'Big'):     # 返回卡號模式mode:[8H10D]十進制、[8H]陣列、[6H]、[SOCA]、[SOYAL]
        self.scan_one_card_UID()                               # 發送讀卡UID指令
        self.get_one_card_data()                               # 讀取卡片資料
        return_UID = self.UID_output(mode = '8H10D', Endianness = 'Big')    #取得卡片UID

        if return_UID == -1:
            print('[No card detected!]')
            return -1
        else:
            print('')
            print('偵測到卡片UID:', return_UID)
            print('')
            return return_UID

    def scan_one_card_UID(self):
        self._i2c.readfrom(self._address, 256)                 # 確保先前命令已接收完畢
        self.cmd_direct(CMD_SCAN_ONE_CARD)                     # 發送讀卡指令

    def get_one_card_data(self):
        self._bytearr = bytearray()                            # byte陣列一定要先清空
        self._bytearr = self.receive_DATA(receive_len = 20)    # 拆解回應包

    def UID_output(self, mode = '8H10D', Endianness = 'Big'):  # 返回卡號模式mode:[8H10D]十進制、[8H]陣列、[6H]、[SOCA]、[SOYAL]
        if self._bytearr == -1:                                # 檢測卡片失敗
            return -1
        UID = self._bytearr[-4:]                               # 取得卡號
        print('UID =', UID)

        # 如果模式為特殊廠商，則強迫設定大頭派或小頭派
        if mode in ['SOCA', 'SOYAL']:
            Endianness = 'Little'

        if Endianness != 'Big':                                # 如果是小頭派(Little)，就反轉列表
            UID = bytes(bytearray([UID[3], UID[2], UID[1], UID[0]]))

        if mode == '8H':
            return_UID = UID[0:4]                                    # 返回卡號(4byte陣列)
        elif mode == '8H10D':
            return_UID = ustruct.unpack("I", UID)[0]                 # 返回卡號(十進制共10位數)
        elif mode == '6H':
            return_UID = UID[1:4]                                    # 返回卡號(3byte陣列)
        elif mode == '6H8D':
            return_UID = ustruct.unpack("I", UID)[0]                 # 返回卡號(十進制共10位數)
        elif mode == 'SOCA':
            return_UID = ustruct.unpack(">BH", UID[1:4])             # 返回卡號(十進制共8位數)
        elif mode == 'SOYAL':                                        # (2H3D+4H5D)
            return_UID = ustruct.unpack(">2H", UID)                  # 返回卡號(十進制共8位數)
        else:                                                        # 未知模式改採預設模式(8H10D)
            print('Unknow mode.Return 8H10D')
            return_UID = ustruct.unpack("I", UID)[0]                 # 返回卡號(十進制共10位數)

        return return_UID

# ======== 喚醒PN532
    def WAKEUP(self):                                           # 直接發送指令
        self._i2c.readfrom(self._address, 20)                   # 確保先前命令已接收完畢
        self._i2c.writeto(self._address, CMD_WAKEUP)            # 送出指令

        self._bytearr = bytearray()                             # byte陣列一定要先清空
        time.sleep_ms(150)                                      # 讀取前一定要等待一段時間，確認資料準備完畢
        self._bytearr = self._i2c.readfrom(self._address, 20)   # 收到回應(應內含握手訊號ACK)

        if PN532_ACK in self._bytearr:                          # 檢查是否存在握手訊號ACK
            print('[PN532 WAKEUP]...OK!')
            DATA = self.receive_DATA(receive_len = 20)          # 解析資料(取得喚醒指令後的回傳資料)
            print('receive DATA =', DATA)
            return 1
        else:
            print('[PN532 WAKEUP]...failure!')
            print('PN532_ACK:', self.byte2str_hex(PN532_ACK))
            print('Please Confirm：', self.byte2str_hex(self._bytearr))
            return -1

# ======== 組裝合成封包
    def direct_combine_DATA(self, DATA):                       # 直接發送指令
        # DATA 一律轉為bytes型態
        type_DATA = type(DATA)
        if type_DATA != bytes:                                 # 輸入為bytes
            if type_DATA == bytearray:                         # 輸入為bytearray
                DATA = bytes(DATA)                             # 轉換輸入型態
            elif type_DATA == str:                             # 輸入為string(必須為hex)
                DATA = self.str_hex2byte(DATA)                 # 轉換輸入型態
            else:
                print('Warring： Please enter \'bytes\', \'bytearray\' or \'string\' (must be hexadecimal) type!')
                return

        PREAMBLE = b'\x00'
        START_CODE = b'\x00\xFF'
        LEN = len(DATA) + 1
        LCS = (LEN ^ 0xFF) + 1
        TFI = b'\xd4'                     # 傳向Card
        DCS = (((sum(DATA[:]) + sum(TFI)) & 0xFF) ^ 0xFF) + 1
        POSTAMBLE = b'\x00'

        return PREAMBLE + START_CODE + bytes([LEN]) + bytes([LCS]) + TFI + DATA + bytes([DCS]) + POSTAMBLE


# ======== 接收並拆解回應封包
    def receive_DATA(self, INPUT = '', receive_len = 256):      # 接收並拆解回應封包
        self._bytearr = bytearray()                             # byte陣列一定要先清空
        time.sleep_ms(150)                                      # 讀取前一定要等待一段時間，確認資料準備完畢
        self._bytearr = self._i2c.readfrom(self._address, receive_len)  # 收到回應

        print('INPUT =', INPUT)
        # 若有輸入INPUT則改為拆解輸入包
        if INPUT != '':                                         # 測試用
            type_DATA = type(INPUT)
            print('type_DATA =', type_DATA)
            self._bytearr = INPUT
            if type_DATA != bytes:                              # 輸入為bytes
                if type_DATA == bytearray:                      # 輸入為bytearray
                    self._bytearr = bytes(INPUT)                # 轉換輸入型態
                elif type_DATA == str:                          # 輸入為string(必須為hex)
                    self._bytearr = self.str_hex2byte(INPUT)     # 轉換輸入型態
                else:
                    print('Warring： Please enter \'bytes\', \'bytearray\' or \'string\' (must be hexadecimal) type!')
                    return
        print('self._bytearr =', self._bytearr)

        # 檢查封包的開頭
        if self._bytearr[0:4] != PN532_FRAME_START:
            print('Packet not found PN532_FRAME_START')
            print('Please Confirm：', self.byte2str_hex(self._bytearr))
            return -1
        print('  [PN532_FRAME_START verification]...succeeded')

        # 檢查封包長度驗證碼
        if self._bytearr[4] + self._bytearr[5] &0xFF != 0:
            print('[\'LEN + LCS\' verification]...failed')
            print('Please Confirm：', self.byte2str_hex(self._bytearr))
            return -1
        print('  [\'LEN + LCS\' verification]...succeeded')

        # 檢查封包資料驗證碼(DATA + TFI)
        DATA = self._bytearr[7: 7 + self._bytearr[4] - 1]
        if (sum(DATA, self._bytearr[6]) & 0xFF + self._bytearr[7 + self._bytearr[4] - 1]) & 0xFF != 0:   
            print('[\'DATA\' + \'TFI\' + \'DCS\' verification]...failed')
            print('Please Confirm：', self.byte2str_hex(self._bytearr))
            return -1
        print('  [\'DATA\' + \'TFI\' + \'DCS\' verification]...succeeded')

        # 檢查封包結尾
        if self._bytearr[7 + self._bytearr[4]] != 0:   
            print('[POSTAMBLE verification]...failed')
            print('Please Confirm：', self.byte2str_hex(self._bytearr))
            return -1
        print('  [POSTAMBLE verification]...succeeded')


        print('  DATA：', self.byte2str_hex(DATA))
        return DATA

# ======== 發送指令
    def cmd_direct(self, CMD):                                 # 直接發送指令
        type_CMD = type(CMD)
        if type_CMD != bytes:                                 # 輸入為bytes
            if type_CMD == bytearray:                         # 輸入為bytearray
                CMD = bytes(CMD)                               # 轉換輸入型態
            elif type_CMD == str:                             # 輸入為string(必須為hex)
                CMD = self.str_hex2byte(CMD)                   # 轉換輸入型態
            else:
                print('Warring： Please enter \'bytes\', \'bytearray\' or \'string\' (must be hexadecimal) type!')
                return

        self._i2c.writeto(self._address, CMD)                   # 送出指令

        self._bytearr = bytearray()                             # byte陣列一定要先清空
        time.sleep_ms(50)                                       # 讀取前一定要等待一段時間，確認資料準備完畢
        self._bytearr = self._i2c.readfrom(self._address, 40)   # 收到回應

        if PN532_FRAME_START in self._bytearr:                  # 檢查是否存在ACK
            print('[Send CMD]...OK!')
        else:
            print('[Send CMD]...failure!')
            print('Please Confirm：', self.byte2str_hex(self._bytearr))
        return


# ======== bytes 與 hex 互換
    def str_hex2byte(self, str_hex):                           # str_hex 字串轉為 bytes
        if type(str_hex) != str:                               # 檢查輸入是否符合字串型態
            print('The DATA type must be string!')
            return

        temp = str_hex.split(' ')                              # 首先先切出16進位的部分存到temp中
        self._bytearr = bytearray()                             # byte陣列一定要先清空
        for i in range(len(temp)):
            if temp[i] != '':
                self._bytearr.append(int('0x' + temp[i], 16))  # 文字轉16進制的數字，再串接
        return bytes(self._bytearr)                            # 轉成bytes格式後再傳回


    def byte2str_hex(self, bytearr):                           # bytes 轉為字串 str_hex
        if type(bytearr) != bytes:                             # 檢查輸入是否符合型態
            if type(bytearr) == bytearray:                     # bytearray直接轉成bytes
                bytearr = bytes(bytearr)
            else:
                print('The type of input must be bytes or bytearray!')
                return

        self._str_hex = ''                                     # 準備輸出字串
        for i in range(len(bytearr)):
            temp = hex(bytearr[i]).replace('0x', '')           # 讀取一個byte，轉成hex後去掉0x
            if len(temp) < 2:                                  # 若字串僅一個字元，則前面補0
                self._str_hex += '0'
            self._str_hex = self._str_hex + temp + ' '         # 串接字串
        return self._str_hex.rstrip(' ').upper()               # 去除結尾的空白後轉成大寫再傳出

# ===============================