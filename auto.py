import datetime
import numpy as np
import mss
import random
import serial
import threading
import time

from MonsterDetector import MonsterDetector

global monsterDetector, screenTop, screenLeft, usb, isBattle, nextSelectMonsterTime, pauseTime, pauseTimeEnd
screenTop = 227
screenLeft = 448
isBattle = False
topLeftPixels = [[80,20], [80, 70], [40, 90], [85, 100], [150, 105]]
topRightPixels = [[890, 100], [800, 65], [830, 110], [875, 120], [775, 135]]
bottomLeftPixels = [[50,625], [80, 620], [20, 625], [100, 630]]
bottomRightPixels = [[940,630], [970,620], [975,600], [910,645]]

leftPixel = [67, 716]
rightPixel = [181, 717]
topPixel = [125, 689]
bottomPixel = [125, 745]
leftMiddlePixel = [94, 731]
rightMiddlePixel = [154, 701]

pauseTime = datetime.datetime.now() + datetime.timedelta(seconds=46*60)
pauseTimeEnd = datetime.datetime.now() + datetime.timedelta(seconds=61*60)

monsterDetector = MonsterDetector()
nextSelectMonsterTime = datetime.datetime.now()
usb = serial.Serial()
usb.baudrate = 9600
usb.port = "COM7"
usb.open()

def mouseMoveClick(button, x, y):
    x = x - int(1024 / 2)
    y = y - int(768 / 2)
    usb.write(("m:"+button+":"+str(x)+":"+str(y)+"\n").encode('utf-8'))

def keyPress(key):
    usb.write(("k:"+key+"\n").encode('utf-8'))

def initBattle(x, y):
    x = x - int(1024 / 2)
    y = y - int(768 / 2)
    time.sleep(0.1)
    usb.write(("b:b:"+str(x)+":"+str(y)+"\n").encode('utf-8'))

def screenCap():
    global screenTop, screenLeft
    with mss.mss() as sct:
        # The screen part to capture
        monitor = {'top': screenTop, 'left': screenLeft, 'width': 1024, 'height': 768}

        # Grab the data
        return np.array(sct.grab(monitor), dtype=np.uint8)

def checkBattleStartingPos(img):
    global leftPixel, rightPixel, topPixel, bottomPixel, leftMiddlePixel, rightMiddlePixel
    if img[leftPixel[1]][leftPixel[0]][0] == 156 and img[leftPixel[1]][leftPixel[0]][1] == 0 and img[leftPixel[1]][leftPixel[0]][2] == 0:
        print('left side')
        return 960, 405
    if img[rightPixel[1]][rightPixel[0]][0] == 156 and img[rightPixel[1]][rightPixel[0]][1] == 0 and img[rightPixel[1]][rightPixel[0]][2] == 0:
        print('right side')
        return 40, 405
    if img[topPixel[1]][topPixel[0]][0] == 156 and img[topPixel[1]][topPixel[0]][1] == 0 and img[topPixel[1]][topPixel[0]][2] == 0:
        print('top side')
        return 500, 600
    if img[bottomPixel[1]][bottomPixel[0]][0] == 156 and img[bottomPixel[1]][bottomPixel[0]][1] == 0 and img[bottomPixel[1]][bottomPixel[0]][2] == 0:
        print('bottom side')
        return 500, 85
    if img[leftMiddlePixel[1]][leftMiddlePixel[0]][0] == 156 and img[leftMiddlePixel[1]][leftMiddlePixel[0]][1] == 0 and img[leftMiddlePixel[1]][leftMiddlePixel[0]][2] == 0:
        print('left middle side')
        return 900, 130
    if img[rightMiddlePixel[1]][rightMiddlePixel[0]][0] == 156 and img[rightMiddlePixel[1]][rightMiddlePixel[0]][1] == 0 and img[rightMiddlePixel[1]][rightMiddlePixel[0]][2] == 0:
        print('right middle side')
        return 80, 590
    return int(1024/2), int(768/2)

def checkStamina(img):
    x = 610 - int(1024 / 2)
    y = 390 - int(768 / 2)
    if img[669][190][0] != 66 or img[669][190][1] != 211 or img[669][190][2] != 165 or img[676][190][0] != 66 or img[676][190][1] != 211 or img[676][190][2] != 165:
        usb.write(("s:s:"+str(x)+":"+str(y)+"\n").encode('utf-8'))
        time.sleep(1.5)

def checkIsBattle(img):
    global isBattle
    if img[3][1004][1] == 199 and img[36][1004][1] == 199 and img[5][988][1] == 199 and img[31][979][1] == 199:
        if isBattle is not False:
            print('Not in battle')
            isBattle = False
            checkStamina(img)
            # time.sleep(random.randint(1,10))

    else:
        if isBattle is not True:
            print('In battle')
            isBattle = True
            time.sleep(2.5)
            px, py = checkBattleStartingPos(screenCap())
            initBattle(px, py)
            print(datetime.datetime.now())

def selectMonster(box, score):
    global nextSelectMonsterTime
    # print(score)
    if (score > 0.7):
        minY = box[0] * 768
        minX = box[1] * 1024
        maxY = box[2] * 768
        maxX = box[3] * 1024
        # print(int(minX + (maxX - minX) / 2), int(minY + (maxY - minY) / 2))
        mouseMoveClick('r', int(minX + (maxX - minX) / 2), int(minY + (maxY - minY) / 2))
        nextSelectMonsterTime = datetime.datetime.now() + datetime.timedelta(seconds=5)

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec) 
        func()  
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def main():
    global isBattle, nextSelectMonsterTime, pauseTime, pauseTimeEnd

    img = screenCap()
    # boxes, scores, classes, num = monsterDetector.get_classification(np.flip(img[:, :, :3], 2))
    # print(boxes[0][0], scores[0][0], classes[0][0], num)
    # print(img[3][1004])
    # print(img[36][1004])
    # print(img[5][988])
    # print(img[31][979])
    checkIsBattle(img)
    if isBattle == False and nextSelectMonsterTime < datetime.datetime.now():
        if pauseTimeEnd < datetime.datetime.now():
            pauseTime = datetime.datetime.now() + datetime.timedelta(seconds=45*60)
            pauseTimeEnd = datetime.datetime.now() + datetime.timedelta(seconds=60*60)
        if pauseTime < datetime.datetime.now() and pauseTimeEnd > datetime.datetime.now():
            return 0
            
        boxes, scores, classes, num = monsterDetector.get_classification(np.flip(img[:, :, :3], 2))
        selectMonster(boxes[0][0], scores[0][0])

initImg = screenCap()
monsterDetector.get_classification(np.flip(initImg[:, :, :3], 2))

t = set_interval(main, 0.5)