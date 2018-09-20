from PIL import ImageGrab, ImageChops, Image
import numpy as np
import cv2
import win32gui
import pyautogui
import time

pyautogui.FAILSAFE = True
hwnd = win32gui.FindWindow(None, '京彩 - Google Chrome')
try :
    left_x, left_y, right_x, right_y = win32gui.GetWindowRect(hwnd)
    print(left_x, left_y, right_x, right_y)
except :
    print("no catch!")

#找位置
'''
while True:
    x, y = pyautogui.position()
    print(x, y)
    time.sleep(2)
'''
#數字顏色
# 1 148 161 161
# 2 250 0 78
# 3 255 70 66
# 4 247 164 92
# 5 0 211 130
# 6 8 193 228
# 7 169 38 225
# 8 57 115 224
# 9 102 115 137
# 10 54 54 54

while True:
    x, y = pyautogui.position()
    print(x, y)
    
    img = ImageGrab.grab(bbox = (left_x, left_y, right_x, right_y))
    img_np = np.array(img)
    color_want = img_np[255, 648, :]
    print(color_want)
    time.sleep(3)
    '''
    img_np[255,648,:] = 0
    frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
    cv2.imshow("screen box", frame)
    cv2.waitKey(0)
    '''
