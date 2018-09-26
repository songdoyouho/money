from PIL import ImageGrab, ImageChops, Image
import numpy as np
import cv2
import win32gui
import pyautogui
import time
import sys
import json

import secret
keys = secret.keys()

from linebot import LineBotApi
from linebot.models import TextSendMessage

my_user_id = "U4a163602a7d66b0494cc38f4824d4d44"
line_bot_api = LineBotApi(keys.line_api_50)

from datetime import datetime

pyautogui.FAILSAFE = True
hwnd = win32gui.FindWindow(None, '京彩 - Google Chrome')
try :
    left_x, left_y, right_x, right_y = win32gui.GetWindowRect(hwnd)
except :
    print("no catch!")

def correct_or_not(flag, open_result, i_vote, rate):
    print("correct or not")
    if open_result == i_vote:
        flag = True
        rate = 1
        print('correct!!!')
    else:
        flag = False
        rate *= 2
        print('fail!!!')

    return flag, rate

def update_result(color_map, open_result):
    print("update result")
    img = ImageGrab.grab(bbox = (left_x, left_y, right_x, right_y))
    img_np = np.array(img)
    color_want = img_np[255, 648, :] # y , x
    color_want = color_want.tolist()
    true_num = color_map.index(color_want) + 1
    print('open number :',true_num) # 1=單 2=雙   
    # get open_result 
    if true_num % 2 == 0:
        open_result = False
    else:
        open_result = True
    time.sleep(1)
    
    return open_result, true_num

def move_to_vote(flag, open_result, i_vote, rate):
    print('vote time!')
    if open_result == True: #單
        i_vote = open_result
        print('vote single')
        pyautogui.moveTo(780, 600) # 單
        pyautogui.click()
    else:
        i_vote = open_result
        print('vote double')
        pyautogui.moveTo(995, 600) # 雙
        pyautogui.click()
    
    time.sleep(1)
    pyautogui.moveTo(1245, 250) # rate
    pyautogui.click()
    pyautogui.press('backspace')
    time.sleep(1)
    pyautogui.typewrite(str(rate))
    print('vote :', rate*5)
    pyautogui.moveTo(1256, 385) # confirm
    pyautogui.click()
    pyautogui.moveTo(565, 490)
    time.sleep(1)
    pyautogui.click()
    pyautogui.moveTo(685, 470)
    time.sleep(1.5)
    pyautogui.click()

    return i_vote

def refresh():
    pyautogui.moveTo(1090, 252)
    pyautogui.click()

    
# 整點開始下注，45秒時封盤
# 算時間
# main
# init 上一次的結果是單 下單數 一倍
flag = True
open_result = True # 單
i_vote = True # 單
rate = 1
yes_count = 0
no_count = 0
color_map = [[148, 161, 161], [250, 0, 78], [255, 70, 66], [247, 164, 92], [0, 211, 130], [8, 193, 228], [169, 38, 225], [57, 115, 224], [102, 115, 137], [54, 54, 54]]

# init
now = datetime.now()
refresh()
time.sleep(2)
open_result, true_num = update_result(color_map, open_result)
i_vote = open_result
i_vote = move_to_vote(flag, open_result, i_vote, rate)

# start loop
time_flag = True
while time_flag:
    now = datetime.now()

    if now.second == 5: # 五秒時開始下注
        print('-----------------------------------------------------')
        print(now.year, now.month, now.day, now.hour, now.minute)
        print('start bot!')
        refresh()
        time.sleep(2)
        open_result, true_num = update_result(color_map, open_result)
        flag, rate = correct_or_not(flag, open_result, i_vote, rate)

        # load open result
        with open('open_data.json', 'r') as r:
            data = json.load(r)
        data.append([str(now.year)+ ':' +str(now.month)+ ':' +str(now.day)+ ':' +str(now.hour)+ ':' +str(now.minute), str(true_num)])
        # save open result
        with open('open_data.json', 'w') as f:
            json.dump(data, f)

        # 統計有沒有中, 有中把fail歸零
        if flag == True:
            yes_count += 1
            print('success :', yes_count)
            no_count = 0
        else:
            no_count += 1
            print('fail :', no_count)

        # send line to me
        send_sth = str(now.year)+ ':' +str(now.month)+ ':' +str(now.day)+ ':' +str(now.hour)+ ':' +str(now.minute)
        if flag == True:
            if i_vote == True:
                send_result = send_sth + 'win '+ str(rate*5) + 'NTD\n' + 'open number:' + str(true_num) + '\n' + 'voted single' + '\n' + 'success:' + str(yes_count)
            else:
                send_result = send_sth + 'win '+ str(rate*5) + 'NTD\n' + 'open number:' + str(true_num) + '\n' + 'voted double' + '\n' + 'success:' + str(yes_count)
        else:
            if i_vote == True:
                send_result = send_sth + 'lose '+ str(int(rate/2*5)) + 'NTD\n' + 'open number:' + str(true_num) + '\n' + 'voted single' + '\n' + 'fail:' + str(no_count)
            else:
                send_result = send_sth + 'lose '+ str(int(rate/2*5)) + 'NTD\n' + 'open number:' + str(true_num) + '\n' + 'voted double' + '\n' + 'fail:' + str(no_count)
        line_bot_api.push_message(my_user_id, TextSendMessage(send_result))

        # check end
        if yes_count == 100:
            time_flag = False
            continue
        if no_count == 10:
            time_flag = False
            continue        

        # voting
        i_vote = move_to_vote(flag, open_result, i_vote, rate)

    else:
        time.sleep(0.5)