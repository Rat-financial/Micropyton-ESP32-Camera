'''
import machine, os, esp_tools_collection, _thread, camera

# 連接WIFI
esp_tools_collection.connect_wifi_and_update_time(default_WIFI = ['Paien iPhoneXs Max', '00000000'], default_priority = False, WIFI_whitelist_csv_path = 'STA_WIFI_setting.csv', WIFI_whitelist_json_path = '/WIFI_setting.json', WIFI_whitelist_control = 'json', WIFI_Retry_Max_batch = 5, RTC_Retry_Max_batch = 5, timezone = +8)

# 純更新時間
esp_tools_collection.RTC_time().update_time(RTC_Retry_Max_batch = 5, timezone = +8)

# 開啟AP
esp_tools_collection.open_AP_and_WebREPL(authmode = 4, AP_essid = 'My_ESP32-Cam', AP_password = '00000000', password = '00000000')

# 啟用相機和記憶卡
CamSD = esp_tools_collection.Camera_and_SDcard(format = camera.JPEG, framesize = camera.FRAME_HD, xclk_freq = camera.XCLK_10MHz, mount_path = '/sd', flip = 1, mirror = 1, saturation = 0, brightness = 0, contrast = 0, quality =  10, whitebalance = 'camera.WB_NONE')     # 建立物件
buf = CamSD.capture()          # 拍照：成功返回拍照內容，失敗返回-1
CamSD.save_to_SD(path = '/', fileNamePrefix = 'sysLogin', extension = '.jpeg', content = buf)     # 存到SD：成功返回1，失敗返回-1

CamSD.SD_list(path = '/')      # 列印SD卡目錄
CamSD.Camera_unmount()         # 卸載Camera
CamSD.SD_unmount()             # 卸載SD卡
#CamSD.SD_mount()               # 掛載SD卡

# 倒數重開機
esp_tools_collection.system_reboot_count(oled, reboot_count = 10, line = 3)
# 系統停止
esp_tools_collection.system_halt()

'''


import time, ntptime, network, webrepl, machine, ubinascii, os, camera, esp_tools_collection, ujson

# === 連接WIFI並校正時間
def connect_wifi_and_update_time(default_WIFI = ['Paien iPhoneXs Max', '00000000'], default_priority = False, WIFI_whitelist_csv_path = '/STA_WIFI_setting.csv',  WIFI_whitelist_json_path = '/WIFI_setting.json', WIFI_whitelist_control = 'json', WIFI_Retry_Max_batch = 5, RTC_Retry_Max_batch = 5, timezone = +8):
    print('連線WIFI，並更新系統時間')

    esp_wifi = esp_tools_collection.esp_WIFI()               # 建立 WIFI物件
    restart_determination = esp_wifi.connect(default_WIFI, default_priority, WIFI_whitelist_csv_path, WIFI_whitelist_json_path, WIFI_whitelist_control, WIFI_Retry_Max_batch)
    # 連線WIFI(預設基地台帳密,預設優先權,白名單路徑,重試次數)

    if restart_determination < 0:
        print('連線網路失敗...')
        return -1

    RTC = esp_tools_collection.RTC_time()                    # 建立 RTC 物件
    restart_determination = RTC.update_time(RTC_Retry_Max_batch, timezone)   # 更新RTC(重試次數, 修改時區)
    if restart_determination != 1:
        print('更新系統時間失敗...')
        return -1
    return 1                                                 # 連網和更新時間均成功則返回1


# === 下載雲端參數
def download_setting(POST_url):
    # POST_url = 'https://script.google.com/a/mcvs.tp.edu.tw/macros/s/AKfycbyi9UiB6wnMyPAVqw6r9M8RYcRec-AFHzt8CffWBQ/exec'
    # 抓雲端設定檔回來
    import prequests as requests
    import gc

    gc.collect()                                 # 回收記憶體，以免不夠用
    gc.mem_free()
    print('回收記憶體；接收雲端參數中...')

    # 論壇：https://forum.micropython.org/viewtopic.php?t=5496
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}         # Http開頭
    upload = {"command": "download_setting"}
    res = requests.post(url = POST_url, json = upload, headers = headers)   # 用json參數才會自動透過ujson.dumps檢查格式
    print(res.text)                              # google回傳網頁
    print('status_code = ', res.status_code)     # 回應狀態碼
    
    # 把json從html中挖回來
    _temp = res.text
    _temp  = _temp.replace('\\x22','\"').replace('\\x5b','[').replace('\\x5d',']').replace('\\x7b','{').replace('\\x7d','}').replace('\\','')   # 替換字元
    start = _temp.find('"userHtml":"')          # 找到userhtml開頭
    end = _temp.find('","ncc":"')               # 找到userhtml結尾
    _temp = _temp[start + 13 : end-3]
    download_json = '{' + _temp + '}'
    print('下載回來的json內容：\n', download_json)      # 列印出下載回來的json內容
    return download_json


# ===== 以下是針對JSON檔備份和讀取=====

'''
# 先設定名稱和路徑
PATH_json = {'SYSTEM':['SYSTEM_setting', '/SYSTEM_setting.json', '1系統主變數'],
               'WIFI':['WIFI_setting',   '/WIFI_setting.json',   '2無線基地台'],
             'MEMBER':['MEMBER_profile', '/MEMBER_profile.json', '3帳號與密碼']}
'''

# === 把下載下來的JSON參數分別存入檔案中(要配合雲端參數)
def write_setting(download_json, PATH_json):
    import gc, ujson
    gc.collect()                                        # 回收記憶體，以免不夠用
    gc.mem_free()
    print('回收記憶體；整理參數中...')

    PATH_json = ujson.loads(ujson.dumps(PATH_json))     # 載入設定檔參數
    print('參數設定檔:', PATH_json)
    download_json = ujson.loads(download_json)          # 載入下載回來的json內容
    print('下載回來的json內容：:', download_json)

    for _temp in iter(PATH_json):
        data = download_json[PATH_json[_temp][0]]       # 讀出資料
        data = ujson.dumps(data)                        # 轉成json
        src = PATH_json[_temp][1]                       # 準備寫入路徑
        f_src = open(src, 'w', encoding='utf-8')        # 開啟來源檔
        f_src.write(data)                               # 把json字串保存入檔案
        f_src.close()                                   # 關閉來源檔
        print('保存 '+ src +' 檔案成功')


# === 從本機讀取全部JSON設定檔
def read_all_setting_from_PATH_json(PATH_json):
    for _temp in iter(PATH_json):
        print(PATH_json[_temp][1])    # 讀取的檔案路徑
        # 將文字轉為變數(locals)，並依序從每個檔案讀JSON為字典，再放入該變數
        locals()[PATH_json[_temp][0]] = esp_tools_collection.read_setting_from_json_file(json_file_path = PATH_json[_temp][1])
        print(PATH_json[_temp][0], '=', locals()[PATH_json[_temp][0]])
        print('\n')

# === 從本機讀取一個JSON設定檔
def read_setting_from_json_file(json_file_path = 'SYSTEM_setting.json'):
    import ujson
    src = json_file_path
    f_src = open(src, 'r', encoding='utf-8')            # 開啟來源檔
    line_str = f_src.readline()                         # 讀取json(一列)
    f_src.close()                                       # 關閉來源檔
    output = ujson.loads(line_str)                      # 載入json
    return output


# === 從本機備份全部JSON設定檔

def copy_all_setting_from_PATH_json(PATH_json, choose = 'backup'):
    for _temp in iter(PATH_json):
        src = PATH_json[_temp][1]                           # 讀取的檔案路徑
        dst = '/' + PATH_json[_temp][0] + '-backup.json'    # 寫入的檔案路徑
        if choose == 'backup':
            copy_file(src, dst)
            print('從' + src + '備份至'+ dst +' 成功')
        else:
            copy_file(dst, src)
            print('從' + dst + '還原至'+ src +' 成功')
    print('')
    return


# === 從本機複製一個檔案
def copy_file(src, dst):

    f_src = open(src, 'r', encoding='utf-8')            # 開啟來源檔
    f_dst = open(dst, 'w', encoding='utf-8')            # 開啟目的檔

    for line_str in iter(f_src):
        f_dst.write(line_str)                           # 逐列保存入檔案

    f_src.close()                                       # 關閉來源檔
    f_dst.close()                                       # 關閉目的檔
    return



# ===== 以下是其他基礎功能函數 =====


# === 開啟AP並開啟WebREPL
def open_AP_and_WebREPL(authmode = 4, AP_essid = 'My_ESP32-Cam', AP_password = '00000000', password = '00000000'):
    import esp_tools_collection,time
    esp_ap = esp_tools_collection.esp_AP(authmode = 4, AP_essid = 'My_ESP32-Cam', AP_password = '00000000')     # 建立AP物件
    esp_ap.WebREPL(password)                                 # 啟動網頁控制(第一次要用putty輸入自訂密碼以啟用)
    return 1


# === 定義蜂鳴器回呼函數(不管要不要用到，一定要有時間參數t)
def buzzer_beep(obj, times = 3, interval = 50):
    buzzer  = obj              # 設定蜂鳴器物件
    for i in range(times):
        buzzer.on()
        time.sleep_ms(interval)
        buzzer.off()
        time.sleep_ms(interval)

# === 定義取回UID的函數(同時寫入全域變數，發出更新請求)
def scan_one_card_UID_return(pn532, buzzer):
    #global renew_return_UID                             # 連結全域變數
    #global renew_UID                                    # 連結全域變數
    pn532.get_one_card_data()                           # 從pn532的記憶體取回卡片資料(要等一段時間再讀取)
    return_UID = pn532.UID_output(mode = '8H10D', Endianness = 'Big')    #換算卡片UID
    if return_UID != -1:
        buzzer_beep(buzzer, 1, 100) # 蜂鳴器響
        print('return_UID =', return_UID)
    else:
        print('NO_UID')
    print('renew_UID, renew_return_UID', renew_UID, renew_return_UID)
    renew_UID = 1                                        # 對全域變數發出UID更新要求
    renew_return_UID = return_UID                        # 將讀到的UID寫入全域變數
    print('renew_UID, renew_return_UID', renew_UID, renew_return_UID)
    return return_UID

# === OLED顯示系統時間 ===
def show_system_time(oled, line = 0, animation = 1, show = 1):
    if animation == 0 and show == 1:
        show_ = 0
    else:
        show_ = show

    strdate = '%02d/%02d' % (time.localtime()[1:3])                # 取出月,日  %d用十進位顯示輸出
    strtime = '%02d:%02d' % (time.localtime()[3:5])                # 取出時,分
    oled.show_text12_Line(strdate, line = line, x =  0, inverse = True , animation = animation, show = show_)      # 顯示反色 月-日
    oled.show_text12_Line(strtime, line = line, x = 64, inverse = False, animation = animation, show = show_)      # 顯示 時:分,overlap疊加

    if animation == 0 and show == 1:      # 一次顯示，避免閃爍
        oled.show()

# === 倒數重開機
def system_reboot_count(oled, reboot_count = 10, line = 3):
    try:
        oled.show_text12_Line('Reboot..', line = line, animation = 1)            # 重開機倒數秒數
        for i in range(reboot_count):
            print('system reboot...' + str(reboot_count - i))
            oled.clear_H16_Line(line = line, x = 96, c = 0, fill = 1, show = 1)
            oled.show_text12_Line( str(reboot_count - i), line = line, x = 96, animation = 0)
            time.sleep_ms(1000)
        oled.clear()
        oled.show_text12_Line('Rebooting..', line = 3, animation = 1)
        print('\nsystem reboot.\n')
        machine.reset()
    except:
        print('[OLED error]...')
        print('system reboot.\n')


# === 系統停止
def system_halt(t = 1):
    print('系統停止system halt...')
    while True:
        time.sleep(t)
        print('.',end = '')


#=======================================

# 建立拍照和SD卡類別
class Camera_and_SDcard():
    def __init__(self, format = camera.JPEG, framesize = camera.FRAME_HD, xclk_freq = camera.XCLK_10MHz, mount_path = '/sd', flip = 1, mirror = 1, saturation = 0, brightness = 0, contrast = 0, quality =  10, whitebalance = camera.WB_NONE):
        self.format = camera.JPEG
        self.framesize = camera.FRAME_HD
        self.xclk_freq = camera.XCLK_10MHz      # Camera的主要設定
        self.mount_path = mount_path            # SD卡的mount路徑
        self.flip = flip                        # 翻轉
        self.mirror = mirror                    # 左/右
        self.saturation = saturation            # 飽和度：-2,2（默認為0）-2灰階
        self.brightness = brightness            # 亮度：-2,2（默認0）2最亮
        self.contrast = contrast                # 對比：-2,2（默認0）2高對比度
        self.quality = quality                  # 優質：10-63越小，表示質量越高
        self.whitebalance = whitebalance        # 白平衡：WB_NONE（默認）WB_SUNNY WB_CLOUDY WB_OFFICE WB_HOME

    def cam_and_SD_mount(self):
        # 嘗試初始化相機
        status = 0                              # 初始化狀態代碼
        _ = self.Camera_mount()                 # 掛載Camera(不存在則會嘗試重新掛載)
        if _ == 1:
            status += 1                         # Camera 成功，狀態代碼權重增加

        # 嘗試初始化SDCard (https://docs.micropython.org/en/latest/library/machine.SDCard.html)
        _ = self.SD_check()                          # 檢查SDCard 是否存在？(不存在則會嘗試重新掛載)
        if _ == 1:
            status += 2                         # SDCard 成功，狀態代碼權重增加

        print('  狀態代碼意義(2兩者均啟動成功，1僅SDCard，0僅Camera，-1兩者均啟動失敗)')
        print('  狀態代碼:', status - 1)
        return status - 1


    def Camera_mount(self):
        try:
            print('開始初始化Camera...')
            camera.deinit()                             # 載入相機：因為只能初始化一次，所以無論如何都先嘗試關閉，再重新初始化
            _ = camera.init(0, format = self.format, framesize = self.framesize, xclk_freq = self.xclk_freq)  # 設定相機啟動
            #camera.flip(1)                             # 翻轉
            #camera.mirror(1)                           # 左/右
            #camera.saturation(0)                       # 飽和度：-2,2（默認為0）-2灰階
            #camera.brightness(0)                       # 亮度：-2,2（默認0）2最亮
            #camera.contrast(0)                         # 對比：-2,2（默認0）2高對比度
            #camera.quality(10)                         # 優質：10-63越小，表示質量越高
            #camera.whitebalance(camera.WB_NONE)        # 白平衡：WB_NONE（默認）WB_SUNNY WB_CLOUDY WB_OFFICE WB_HOME
            camera.flip(self.flip)                      # 翻轉
            camera.mirror(self.mirror)                  # 左/右
            camera.saturation(self.saturation)          # 飽和度：-2,2（默認為0）-2灰階
            camera.brightness(self.brightness)          # 亮度：-2,2（默認0）2最亮
            camera.contrast(self.contrast)              # 對比：-2,2（默認0）2高對比度
            camera.quality(self.quality)                # 優質：10-63越小，表示質量越高
            camera.whitebalance(self.whitebalance)      # 白平衡：WB_NONE（默認）WB_SUNNY WB_CLOUDY WB_OFFICE WB_HOME
            print(_)
            print('  Camera初始化成功.')
            return 1                                    # SDCard 初始化成功，返回1
        except:
            print('  Camera初始化失敗.')
            return -1                                   # SDCard 初始化失敗，返回-1

    def Camera_unmount(self):
        try:
            print('卸載Camera...')
            camera.deinit()
            print('  卸載Camera成功.')
            return 1
        except:
            print('  卸載Camera失敗.')
            return -1

    def SD_unmount(self):
        try:
            os.umount(self.mount_path)
        except:
            print('',end = '')

        try:
            machine.SDCard.deinit(self.sd)
            del self.sd
        except:
            print('',end = '')

        print('    卸載SD卡完成.')
        return

    def SD_mount(self):
        # 嘗試初始化SDCard (https://docs.micropython.org/en/latest/library/machine.SDCard.html)
        print('  建立新的SDCard物件.')
        try:
            self.sd = machine.SDCard()          # ESP32-Cam 使用預設slot 1腳位就好，否則會變極慢
        except:
            print('',end='')

        try:
            os.mount(self.sd, self.mount_path)  # 要卸載使用 os.umount('/sd')
            print('    SDCard初始化成功.')
            return 1                            # SDCard 初始化成功，返回1
        except:
            print('    SDCard初始化失敗.')
            return -1                           # SDCard 初始化失敗，返回-1

    def SD_check(self):
        try:
            fileName = self.mount_path + '/test.txt'
            with open(fileName, 'w') as f:      # 開啟檔案
                f.write('test')                 # 把資料寫入SDCard
                f.close()                       # 關閉檔案
            f_size = os.stat(fileName)[6]       # 取得檔案大小(byte)
            if f_size <= 0:
                print('  寫入SD卡檔案大小異常.')
                raise Exception('')

            print('  SDCard讀取正常，程式繼續運行.')
            return 1                            # SDCard 初始化成功，返回1
        except:
            print('  SDCard無法讀取，將進行重新初始化...')
            self.SD_unmount()                   # 先卸載SDCard
            _ = self.SD_mount()                 # 再掛載SDCard
            return _


    def SD_list(self, path = '/'):
        try:
            print('讀取輸出目前SDCard卡檔案列表...')
            _ = os.listdir(self.mount_path + path)
            print('  讀取SDCard卡內容成功.')
            return _
        except:
            print('  讀取SDCard卡內容失敗.')
            return -1

    def capture(self):
        try:
            print('拍攝一張照片到buf...',end='')
            buf = camera.capture()
            if buf == False:
                print('相機錯誤.')
                _ = self.Camera_mount()
                if _ == 1:
                    print('  重新掛載Camera成功.繼續執行拍照.')
                    buf = camera.capture()
                    print('  拍照完成.')
                else:
                    print('  重新掛載Camera失敗.請重新檢查連線')
                    return -1
            print('  拍照成功.返回拍照內容.')
            return buf

        except:
            print('  相機發生嚴重錯誤，請檢查.')
            return -1



    def save_to_SD(self, path = '/', fileNamePrefix = 'sysLogin', extension = '.jpeg', content = ''):
        try:
            print('檢查SDCard 是否存在？')           # 不存在則會自動嘗試重新掛載
            _ = self.SD_check()

            if _ == 1:
                print('  SD_check成功.繼續將照片資料寫入SDCard中...', end = '')

                #建立欲儲存的檔名及路徑
                localtime = time.localtime()        # 取得系統時間
                fileName = fileNamePrefix           # 檔名前綴fileName
                for i in range(6):                  # 組成路徑，加上年月日時分秒
                    fileName = fileName  +  '-' + str(localtime[i])

                _temp = path.strip('/')             # 去掉path引數前後的斜線，再重組
                if _temp != '':
                    _temp = '/' + _temp

                # 存檔
                fileName = self.mount_path + _temp + '/' + fileName + extension   # 組合路徑與檔名
                with open(fileName, 'w') as f:      # 開啟檔案
                    f.write(content)                # 把之前拍照的buf資料寫入SDCard
                    f.close()                       # 關閉檔案

                # 檢查存檔狀況
                f_size = os.stat(fileName)[6]       # 取得檔案大小(byte)
                if f_size <= 0:
                    print('  寫入SD卡檔案大小異常.')
                    return -1
                else:
                    print('  寫入SD卡檔案成功.')
                    print('  寫入SD卡的照片檔案大小: {} k'.format(round(f_size/1024, 1)))
                    print('  寫入路徑：', fileName)
                    return 1
            else:
                print('  SD_check失敗，放棄儲存.')
                return -1

        except:
            print('  SD卡發生嚴重錯誤，請檢查.')
            return -1


#===========================================
# 建立AP和WebREPL連線類別
class esp_AP():
    def __init__(self, authmode = 4, AP_essid = 'My_ESP32-Cam', AP_password = '00000000'):
        self.ap = network.WLAN(network.AP_IF)                # 建立 AP:作為熱點讓其他設備連線(才能登入使用webrepl)
        print('開啟AP:', self.ap.active(True))               # 開啟 AP
        self.ap.config(authmode = 4, essid = AP_essid, password = AP_password)    #authmode,0=open, 4=WPA/WPA2-PSK加密(https://kknews.cc/zh-tw/tech/89b293q.html)
        print('AP網路資訊:', self.ap.ifconfig())             # 顯示(IP, netmask, gateway, 與 DNS)
        # 連線網址：https://micropython.org/webrepl/?#192.168.4.1:8266/
        print('已建立 AP 物件')

    def WebREPL(self, password = '00000000'):
        webrepl.start(password)                              # 啟動網頁控制(第一次要用putty輸入自訂密碼以啟用)
        AP_Status = self.ap.ifconfig()
        print('\nREPL:', str(AP_Status[0]) + ':8266')
        print('Password:', password)
        print('已建立 REPL')


#===========================================
# 建立Wifi連線類別
class esp_WIFI():
    def __init__(self):
        self._sta = network.WLAN(network.STA_IF)             # STA:啟用無線介面(AP)，並設定別名以控制
        #self._sta.disconnect()                              # 先斷開STA
        time.sleep_ms(50)
        print('STA開啟狀態：', self._sta.active(True))       # 開啟STA
        print('已建立WIFI物件')

# 連線WIFI(預設基地台帳密,預設優先權,白名單路徑,重試次數)
    def connect(self, default_WIFI = ['Paien iPhoneXs Max', '00000000'], default_priority = False, WIFI_whitelist_csv_path = 'WIFI_setting.csv', WIFI_whitelist_json_path = 'WIFI_setting.json', WIFI_whitelist_control = 'json', WIFI_Retry_Max_batch = 5):
        print('預設的連線基地台名稱、密碼:', default_WIFI)
        print('讀取設定檔的控制:', WIFI_whitelist_control)

        if WIFI_whitelist_control == 'json':
            WIFI_whitelist_path = WIFI_whitelist_json_path    # 載入白名單路徑
            STA_WIFI_DATA = self.load_whitelist_json(default_WIFI, WIFI_whitelist_path)   # 載入白名單
        else:
            WIFI_whitelist_path = WIFI_whitelist_csv_path     # 載入白名單路徑
            STA_WIFI_DATA = self.load_whitelist_csv(default_WIFI, WIFI_whitelist_path)    # 載入白名單

        print('預設最大重複嘗試次數:', WIFI_Retry_Max_batch)
        print('\n目前可用白名單基地台：', STA_WIFI_DATA ,'\n')

        self.disconnect()
        time.sleep_ms(200)
        ans = self.try_connect(STA_WIFI_DATA, default_WIFI, default_priority, WIFI_Retry_Max_batch)
        return ans

# 從檔案載入白名單
    def load_whitelist_csv(self, default_WIFI, WIFI_whitelist_csv_path):
        #----- 載入網路帳號密碼的csv檔 -----
        default_STA = default_WIFI                                     # 預設無線網路帳號密碼
        STA_WIFI_PATH = WIFI_whitelist_csv_path                         # WIFI設定檔路徑
        STA_WIFI_DATA = []                                             # 建立WIFI帳密名單：STA_WIFI_DATA

        #載入STA_WIFI_PATH
        try:                                                           # 需要被監控是否會出錯的程式區塊
            src = STA_WIFI_PATH                                        # 從檔案讀取
            print('WIFI白名單檔讀取路徑:', src)
            f_src = open(src, 'r', encoding='utf-8')                   # 開啟來源檔
            print('開始逐列讀取，去掉斷行符號')
            for line in range(len(open(src, 'rU').readlines())):       # 逐列讀取，去掉斷行符號
                line_Str = f_src.readline()
                line_Str = line_Str.strip()                            # 去除\n\r
                print(line, line_Str)
                STA_WIFI_DATA.append(line_Str.split(','))
            f_src.close()                                              # 關閉來源檔

            print('\n去除標題列...')
            print('將預設連線基地台放入白名單內:', default_STA)
            del STA_WIFI_DATA[0]                                       # 去除標題列
            STA_WIFI_DATA.append(default_STA)                          # 將預設連線基地台放入待比對連線基地台白名單內(放最後面)
            print('載入成功:待比對連線基地台白名單STA_WIFI_DATA，共 {} 個\n'.format(len(STA_WIFI_DATA)))

        except:                                                        # 出了哪種錯誤，要有怎樣相對應的處理
            print('注意：不存在白名單路徑，啟用預設值....\n', '預設連線基地台帳密:', default_WIFI, '\n')
            STA_WIFI_DATA = default_WIFI                               # 沒檔案的話，載入預設值

        return STA_WIFI_DATA

# 從檔案載入白名單
    def load_whitelist_json(self, default_WIFI, WIFI_whitelist_json_path):
        #----- 載入網路帳號密碼的csv檔 -----
        default_STA = default_WIFI                                     # 預設無線網路帳號密碼
        STA_WIFI_PATH = WIFI_whitelist_json_path                       # WIFI設定檔路徑
        STA_WIFI_DATA = []                                             # 建立WIFI帳密名單：STA_WIFI_DATA

        #載入STA_WIFI_PATH
        try:                                                           # 需要被監控是否會出錯的程式區塊
            src = STA_WIFI_PATH                                        # 從檔案讀取
            print('WIFI白名單(json)檔讀取路徑:', src)
            f_src = open(src, 'r', encoding='utf-8')                   # 開啟來源檔
            line_str = f_src.readline()                                # 讀取json(一列)
            f_src.close()                                              # 關閉來源檔

            print('\n載入json...')
            _temp = ujson.loads(line_str)                              # 從JSON載入為字典(來源必要是字串)

            for _ in iter(_temp):                                      # 取出基地台帳號密碼
                DATA = [_]
                DATA.extend(_temp[_])
                STA_WIFI_DATA.append(DATA)

            print('STA_WIFI_DATA =', STA_WIFI_DATA)
            print('將預設連線基地台放入待比對連線基地台白名單內(放最後面)')
            STA_WIFI_DATA.append(default_STA)
            print('待比對連線基地台白名單:', STA_WIFI_DATA)
            print('載入成功:待比對連線基地台白名單STA_WIFI_DATA，共 {} 個\n'.format(len(STA_WIFI_DATA)))

        except:                                                        # 出了哪種錯誤，要有怎樣相對應的處理
            print('注意：不存在白名單路徑，啟用預設值....\n', '預設連線基地台帳密:', default_WIFI, '\n')
            STA_WIFI_DATA = default_WIFI                               # 沒檔案的話，載入預設值

        return STA_WIFI_DATA


    def disconnect(self):                                              # 斷開STA
        self._sta.disconnect()
        print('關閉WIFI連線...')
        return

# 嘗試連線WIFI(白名單,預設基地台帳密,預設優先權,重試次數)
    def try_connect(self, STA_WIFI_DATA, default_WIFI, default_priority, WIFI_Retry_Max_batch):
        # 回傳值-1代表連線失敗，回傳值0代表當前已處於連線狀態，回傳值1代表連接成功

        if self._sta.isconnected():                                                # 檢查當前是否處於連線狀態
            print('WIFI已處於連線狀態.')
            print('STA網路資訊:', self._sta.ifconfig())                            # 顯示(IP, netmask, gateway, 與 DNS)
            return 0                                                               # 回傳值 0 代表當前已處於連線狀態

        #----- 依目前有訊號的基地台建立清單，開始嘗試連線 -----
        Retry_Max = WIFI_Retry_Max_batch                                           # 設定最大重試批次數
        Retry = 0                                                                  # 目前重試批次數

        while Retry <= Retry_Max:
            if Retry == Retry_Max:                                                 # 達 Retry_Max 次就放棄，自動重新開機
                print('重試已達 {} 次循環. 放棄嘗試...'.format(Retry))
                return -1                                                          # 回傳-1代表連線失敗
                #time.sleep_ms(1000)                                                # 等待一秒來告知使用者
                #machine.reset()                                                    # 硬體方式重啟系統

            else:                                                                  # 如果是重新循環的開始且未連接上線，則再次建立欲嘗試的基地台清單
                if not self._sta.isconnected():                                    # 檢查是否已連接上線？
                    Retry += 1 
                    print('正在嘗試第 {} 次循環:'.format(Retry))                   # 顯示已嘗試第幾批次
                    time.sleep_ms(300)                                             # 再嘗試下一批次的時間間隔

                    #----- 更新可嘗試的基地台清單 -----
                    print('\n正在掃描現場基地台強度(按強弱排序)...請稍待')
                    STA_NOW = self._sta.scan()                                     #(ssid，硬體地址bssid，通道，強度RSSI，加密authmode，隱藏)
                    if STA_NOW == []:                                              # 如果一台基地台都沒有，嘗試先斷線再重新掃描
                        self._sta.disconnect()
                        STA_NOW = self._sta.scan()
                    print('現場基地台STA_NOW：，共 {} 個：\n{}'.format(len(STA_NOW), STA_NOW))

                    _TEMP = STA_WIFI_DATA.copy()                                   # 重新備妥比對名單(注意：至少要用淺複製copy方法！)

                    # 更新欲嘗試的基地台清單(有訊號且在已知清單上)：STA_CONNECT_DATA
                    print('\n正在建立欲嘗試的基地台清單...請稍待')
                    STA_CONNECT_DATA = []                                          # 清空嘗試連線列表
                    for i in range(len(STA_NOW)):
                        for j in range(len(_TEMP)):
                            if STA_NOW[i][0].decode('utf-8') == _TEMP[j][0]:       # 如果 該基地台在已知的基地台名稱清單中
                                STA_CONNECT_DATA.append(_TEMP[j])                  # 把該基地台的名稱和密碼加入嘗試連線列表
                                del _TEMP[j]                                       # 比對正確就從比對名單移入嘗試連線列表，並離開該輪比對迴圈
                                break
                    print('已更新可嘗試的基地台清單STA_CONNECT_DATA，共 {} 個：\n{}'.format(len(STA_CONNECT_DATA), STA_CONNECT_DATA))

                    # 若預設基地台優先權啟動，則將其移至最優先位置
                    if default_priority == True:
                        try:
                            STA_CONNECT_DATA.remove(default_WIFI)                 # 移除預設基地台
                            STA_CONNECT_DATA.insert(0, default_WIFI)              # 將預設基地台放到列表最前面

                        except:                                                   # 出了哪種錯誤，要有怎樣相對應的處理
                            print('預設基地台不在目前可見的基地台列表中.')

                    # 檢查是否完全沒有可連線的基地台
                    if len(STA_CONNECT_DATA) == 0:
                        print('找不到任何在白名單上的基地台，目前已嘗試{}/{}次'.format(Retry, Retry_Max))
                        #time.sleep_ms(1000)                                                             # 等待一段時間來告知使用者

                else:
                    print('已連接上:', STA_CONNECT_DATA[i][0])     # 顯示成功連接的基地台
                    STA_Status = self._sta.ifconfig()              # 取得(IP, netmask, gateway, 與 DNS)
                    print('STA網路資訊:', STA_Status)              # 顯示(IP, netmask, gateway, 與 DNS)
                    return 1                                       # 回傳 1 代表連線成功
                    #break

                print('開始逐個嘗試連接基地台...')
                # 每次循環依欲嘗試的基地台清單，開始逐個嘗試連接
                for i in range(0, len(STA_CONNECT_DATA)):                                               # 逐列測試連線Wifi基地台
                    print('\nTry to connect...', '{}/{}'.format(i+1, len(STA_CONNECT_DATA)) )
                    print('STA:', STA_CONNECT_DATA[i][0], '   Password:', STA_CONNECT_DATA[i][1])

                    try:
                        self._sta.connect(STA_CONNECT_DATA[i][0], STA_CONNECT_DATA[i][1])                   # STA：設定連接熱點(SSID,Password)
                    except:
                        print('Wifi Internal Error.Try again.')

                    count = 0                                      # 每個基地台有 10 次可嘗試等待回應，有得到 IP 就離開迴圈
                    while not self._sta.isconnected():             # 檢查：若尚未連接上網路
                        print('count=', count)
                        time.sleep_ms(800)                         # 等待回應(隔多久再詢問)
                        count += 1
                        if count == 10:                            # 每個基地台最多詢問次數
                            break

                    if self._sta.isconnected():                    # 一旦連接上，就不必再嘗試其他的基地台了
                        break

                    time.sleep_ms(100)                             # 轉換基地台的時間間隔
            time.sleep_ms(500)
        return 1

#===========================================
# 建立RTC時間類別
class RTC_time():
    def __init__(self):
        print('已建立 RTC 物件')

    def update_time(self, RTC_Retry_Max_batch = 5, timezone = +8):
        ans = self.load_GMT_time(RTC_Retry_Max_batch)                              # 透過網路更新 GMT 時間
        if ans == -1:
            print('更新時間失敗...')
            return -1
        else:
            self.change_time_zone(timezone)                                        # 網路時間更新成功，繼續調整時區
            return 1

    def load_GMT_time(self, RTC_Retry_Max_batch = 5):
        Retry_Max = RTC_Retry_Max_batch                                            # 設定最大重試批次數
        Retry = 0                                                                  # 目前重試批次數

        while Retry < Retry_Max:
            try:                                                                   # 需要被監控是否會出錯的程式區塊
                print('\n---透過網路 NTP 伺服器取得 GMT 時間---')
                ntptime.settime()                                                  # settime函數會自 NTP 伺服器取得之 UTC 時間設定 RTC

            except:                                                                # 出了哪種錯誤，要有怎樣相對應的處理
                print('時間載入失敗，目前共重試 {} 次...'.format(Retry))

                if Retry+1 == Retry_Max:                                           # 超過 Retry_Max 次就放棄，自動重新開機
                    print("重試已超過 {} 次. 請檢查網路狀態...".format(Retry+1))
                    return -1                                                      # 回傳值 -1 代表查詢網路時間失敗

            else:                                                                  # 都沒錯誤，就會執行此區塊的程式
                print('時間載入成功')
                print('累計共重試 {} 次...'.format(Retry))
                break                                                              # 已獲得時間則離開while迴圈

            finally:                                                               # 不論如何都會執行此區塊的程式
                Retry += 1

        #print('模組時間(年,月,日,時,分,秒,星期,今年第幾天):', time.localtime())    # 從time函數讀取模組時間localtime(等同gmtime，均只能讀)
        print('已取得GMT(+0) 時間:', machine.RTC().datetime())                     # 從machine呼叫系統時間datetime(要用machine.RTC才能改)
        return 1                                                                   # 回傳值 1 代表查詢網路時間成功

    def change_time_zone(self, timezone = +8):
        # 更改系統時區(以machine.RTC為準)
        print('\n---依時區更新系統時間，台灣時區(GMT+8)---')
        tm = time.localtime()                                                      # 模組時間 localtime 格式:(年,月,日,時,分,秒,星期,今年第幾天)
        tm = tm[0:3] + (0,) + (tm[3] + int(timezone),) + tm[4:6] + (0,)            # 更改為datetime 格式:同時修改時區，準備送給 RTC 設定系統時間
        machine.RTC().datetime(tm)                                                 # 寫入系統時間 RTC().datetime，星期和天數都會自動調整

        print('系統時間(年,月,日,星期,時,分,秒,毫秒)主格式:', machine.RTC().datetime())  # 從machine讀取系統時間datetime
        #print('GMT 時間(年,月,日,時,分,秒,星期,今年第幾天):', time.gmtime())      # 從time函數讀取 gmt時間(等同localtime)
        #print('模組時間(年,月,日,時,分,秒,星期,今年第幾天):', time.localtime())   # 從time函數讀取模組時間localtime(等同gmtime，均只能讀)
        print('')
        return 1                                                                   # 回傳值 1 代表查詢網路時間成功

