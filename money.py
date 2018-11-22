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

def update_result(color_map):
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

def vote_loop(win_count, last_open):
    # start vote loop
    time_flag = True
    vote_flag = True # 有沒有猜對
    vote_open_result = last_open # 開獎結果，單
    vote_i_vote = last_open # 我下的，單
    vote_rate = 1
    vote_yes_count = 0
    vote_no_count = 0

    while time_flag:
        now = datetime.now()

        if now.second == 13:
            print('-----------------------------------------------------')
            print(now.year, now.month, now.day, now.hour, now.minute)
            print('start bot!')
            refresh()
            time.sleep(2)
            vote_open_result, vote_true_num = update_result(color_map)
            vote_flag, vote_rate = correct_or_not(vote_flag, vote_open_result, vote_i_vote, vote_rate)

            # 統計有沒有中, 有中把fail歸零
            if vote_flag == True:
                vote_yes_count += 1
                print('success :', vote_yes_count)
                vote_no_count = 0
            else:
                vote_no_count += 1
                print('fail :', vote_no_count)

            # send line to me
            send_sth = str(now.year)+ ':' +str(now.month)+ ':' +str(now.day)+ ':' +str(now.hour)+ ':' +str(now.minute)
            if vote_flag == True:
                if vote_open_result == True:
                    send_result = send_sth + '\n' + 'win '+ '\n' + 'open number:' + str(vote_true_num) + '\n' + 'voted single' + '\n' + 'success:' + str(vote_yes_count)
                else:
                    send_result = send_sth + '\n' + 'win '+ '\n' + 'open number:' + str(vote_true_num) + '\n' + 'voted double' + '\n' + 'success:' + str(vote_yes_count)
            else:
                if vote_open_result == True:
                    send_result = send_sth + '\n' + 'lose '+ '\n' + 'open number:' + str(vote_true_num) + '\n' + 'voted single' + '\n' + 'fail:' + str(vote_no_count)
                else:
                    send_result = send_sth + '\n' + 'lose '+ '\n' + 'open number:' + str(vote_true_num) + '\n' + 'voted double' + '\n' + 'fail:' + str(vote_no_count)
            
            line_bot_api.push_message(my_user_id, TextSendMessage(send_result))

            # check end
            if vote_yes_count == win_count:
                time_flag = False
                continue
            if vote_no_count == 7:
                time_flag = False
                continue        

            # voting
            vote_i_vote = move_to_vote(vote_flag, vote_open_result, vote_i_vote, vote_rate)
        else:
            time.sleep(0.5)

# 整點開始下注，45秒時封盤
# 算時間
# main
# init 上一次的結果是單 下單數 一倍
flag = True
open_result = True # 單
i_vote = True # 單
rate = 1
no_count = 0
color_map = [[148, 161, 161], [250, 0, 78], [255, 70, 66], [247, 164, 92], [0, 211, 130], [8, 193, 228], [169, 38, 225], [57, 115, 224], [102, 115, 137], [54, 54, 54]]

# init

now = datetime.now()
refresh()
time.sleep(2)
open_result, true_num = update_result(color_map)
last_open = open_result
last_num = true_num

# start loop
while True:
    now = datetime.now()

    if now.second == 10: 
        if no_count == 6:
            line_bot_api.push_message(my_user_id, TextSendMessage('沒中6次!\n準備開始下注!'))

            # 繼續監視連撞是否結束
            watch_flag = True
            while watch_flag:
                now = datetime.now()
                if now.second == 9:
                    refresh()
                    time.sleep(2)
                    open_result, true_num = update_result(color_map)
                    # 統計有沒有中, 有中把fail歸零
                    if last_open == open_result: # 上一次開的跟這一次一樣
                        line_bot_api.push_message(my_user_id, TextSendMessage('上次開'+str(last_num)+'號\n'+'這次開'+str(true_num)+'號\n'+'結束監視!'))
                        watch_flag = False # 結束監視
                    else:
                        no_count += 1
                        line_bot_api.push_message(my_user_id, TextSendMessage('上次開'+str(last_num)+'號\n'+'這次開'+str(true_num)+'號\n'+'還是沒中'+str(no_count)+'次!'))

                    last_open = open_result
                    last_num = true_num

            no_count = 0
            # 開始下注
            line_bot_api.push_message(my_user_id, TextSendMessage('開始下注!'))
            vote_loop(6, last_open)
        else:
            refresh()
            time.sleep(2)
            open_result, true_num = update_result(color_map)

            # 統計有沒有中, 有中把fail歸零
            if last_open == open_result: # 上一次開的跟這一次一樣
                no_count = 0
            else:
                no_count += 1
                line_bot_api.push_message(my_user_id, TextSendMessage('上次開'+str(last_num)+'號\n'+'這次開'+str(true_num)+'號\n'+'沒中'+str(no_count)+'次!'))

            last_open = open_result
            last_num = true_num
    else:
        time.sleep(0.5)