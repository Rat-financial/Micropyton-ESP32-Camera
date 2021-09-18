import machine
import time
from machine import PWM, Pin
from time import sleep

servo = PWM(Pin(2), freq=50)  # 頻率每秒50次，每單位週期為20ms(=1000/50)
 
period = 20000   # SG90伺服馬達的PWM訊號週期約為20ms，方便計算放大1000倍
minDuty = int(500/period *1024)   # SG90的最小高電位訊號間隔0.5ms，設為500
maxDuty = int(2400/period *1024)  # SG90的最大高電位訊號間隔0.5ms，設為2400
unit = (maxDuty - minDuty)/180    # 可接受數值範圍為500~2400中，控制180度，計算每一度的數值
 
def rotate(servo, degree=0):      # 轉幾度副程式(servo, degree角度)
    _duty = round(unit * degree) + minDuty    # 計算使用者輸入的角度應設定的值
    _duty = min(maxDuty, max(minDuty,_duty))  # 檢查有無錯誤(保持數值在可動範圍內)
    servo.duty(_duty)    
 
def SG90():
    rotate(servo, 0)            # 轉到0度
    sleep(0.5)
    rotate(servo, 90)           # 轉到90度
    sleep(1)
    rotate(servo, 0)          # 轉到0度

    
 



