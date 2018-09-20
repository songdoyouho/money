from PIL import ImageGrab, ImageChops, Image
import numpy as np
import cv2
import win32gui
import pyautogui
import time
import sys
import json
from datetime import datetime

from datetime import datetime

pyautogui.FAILSAFE = True
hwnd = win32gui.FindWindow(None, '京彩 - Google Chrome')
try :
    left_x, left_y, right_x, right_y = win32gui.GetWindowRect(hwnd)
except :
    print("no catch!")

def refresh():
    pyautogui.moveTo(1090, 252)
    pyautogui.click()

def update_result(color_map):
    print("update result")
    img = ImageGrab.grab(bbox = (left_x, left_y, right_x, right_y))
    img_np = np.array(img)
    color_want = img_np[255, 648, :] # y , x
    color_want = color_want.tolist()
    true_num = color_map.index(color_want) + 1
    print('open number :',true_num) # 1=單 2=雙       
    return true_num
    
color_map = [[148, 161, 161], [250, 0, 78], [255, 70, 66], [247, 164, 92], [0, 211, 130], [8, 193, 228], [169, 38, 225], [57, 115, 224], [102, 115, 137], [54, 54, 54]]

# start loop
time_flag = True
while time_flag:
    now = datetime.now()

    if now.second == 5: # 五秒時開始
        refresh()
        true_num = update_result(color_map)
        # load open result
        with open('open_result.json', 'r') as r:
            data = json.load(r)
        data.append([str(now.year)+ ':' +str(now.month)+ ':' +str(now.day)+ ':' +str(now.hour)+ ':' +str(now.minute), str(true_num)])
        # save open result
        with open('open_result.json', 'w') as f:
            json.dump(data, f)

        time.sleep(5)