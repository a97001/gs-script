from PIL import Image
import datetime
import numpy as np
import mss
import pytesseract
import serial
import threading
import time
import win32gui

# pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
tessdata_dir_config = '--tessdata-dir "C:\\Program Files\\Tesseract-OCR\\tessdata" -l eng --psm 6 --oem 3'

screenTop = 227
screenLeft = 448

# from MonsterDetector import MonsterDetector
def callback(hwnd, windowSize):
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    if (win32gui.GetWindowText(hwnd) == 'Gersang'):
        print("Window %s:" % win32gui.GetWindowText(hwnd))
        print("\tLocation: (%d, %d)" % (x, y))
        print("\t    Size: (%d, %d)" % (w, h))
        windowSize.append(y + 26)
        windowSize.append(x + 3)

windowSize = []
win32gui.EnumWindows(callback, windowSize)
if (len(windowSize) > 0):
    screenTop = windowSize[0]
    screenLeft = windowSize[1]
print("\t    Actual Pos: (%d, %d)" % (screenLeft, screenTop))

def screenCapRect(top, left, width, height):
    global screenTop, screenLeft
    with mss.mss() as sct:
        # The screen part to capture
        monitor = {'top': screenTop+top, 'left': screenLeft+left, 'width': width, 'height': height}

        # Grab the data
        return np.array(sct.grab(monitor), dtype=np.uint8)

def imageORC(img):
    tessdata_dir_config = '--tessdata-dir "C:\\Program Files\\Tesseract-OCR\\tessdata" -l eng --psm 6 --oem 3 -c load_system_dawg=0 -c load_freq_dawg=0'
    data = np.copy(img)
    for y in range(len(data)):
        for x in range(len(data[y])):
            # if data[y][x][0] != 255:
            #     data[y][x][0] = 0
            if data[y][x][1] != 251:
                data[y][x][1] = 0
            # if data[y][x][2] != 255:
            #     data[y][x][2] = 0

    image = Image.fromarray(data)
    width = 1000
    ratio = float(width)/image.size[0]
    height = int(image.size[1]*ratio)
    image = image.resize( (width, height), Image.BILINEAR)
    try:
        s = pytesseract.image_to_string(image, config=tessdata_dir_config)
        return s
    except:
        return ''

# with mss.mss() as sct:
#     # The screen part to capture
#     monitor = {'top': screenTop, 'left': screenLeft, 'width': 1024, 'height': 768}

#     # Grab the data
#     img = np.array(sct.grab(monitor))
#     print(img.shape)
#     img = np.flip(img[:, :, :3], 2)
#     print(img.shape)
#     # boxes, scores, classes, num = monsterDetector.get_classification(img[:,:,:3])
#     # print(boxes[0][0], scores[0][0], classes[0][0], num)
#     # print(img[3][1004])
#     # print(img[36][1004])
#     # print(img[5][988])
#     # print(img[31][979])

# image = Image.open('C:\\Users\\comon\\Desktop\\gs\\testrec.jpg')
# image = image.convert('RGB')
# data = np.array(image)
# for y in range(len(data)):
#     for x in range(len(data[y])):
#         # if data[y][x][0] != 255:
#         #     data[y][x][0] = 0
#         if data[y][x][1] != 251:
#             data[y][x][1] = 0
#         # if data[y][x][2] != 255:
#         #     data[y][x][2] = 0

# image = Image.fromarray(data)
# width = 1000
# ratio = float(width)/image.size[0]
# height = int(image.size[1]*ratio)
# image = image.resize( (width, height), Image.BILINEAR  )

# image = image.filter(ImageFilter.FIND_EDGES)

# image = ImageEnhance.Contrast(image).enhance(100)
 
# image = ImageEnhance.Color(image).enhance(0)
# image = ImageEnhance.Sharpness(image).enhance(3)    
# image.show()

# s = pytesseract.image_to_string(image, config=tessdata_dir_config)
# print(s)
# print(eval(s.replace('x', '*')))

img = screenCapRect(708, 837, 55, 17)
# image = Image.fromarray(img)
# image.show()
s = imageORC(img)
print(s)
print('-------end-------')
