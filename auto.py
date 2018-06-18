from PIL import Image
import datetime
import numpy as np
import mss
import pytesseract
import random
import serial
import threading
import time

from MonsterDetector import MonsterDetector

global monsterDetector, screenTop, screenLeft, mapIconColor, battleColor, mouseRatio, usb, isBattle, nextSelectMonsterTime, pauseTime, pauseTimeEnd
screenTop = 227
screenLeft = 448
isBattle = False
battleColor = 148
mouseRatio = 1

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

def parseInt(string):
    return int(''.join([x for x in string if x.isdigit()]))

def mouseMoveClick(button, x, y):
    global mouseRatio
    x = int((x - 1024 / 2) * mouseRatio)
    y = int((y - 768 / 2) * mouseRatio)
    usb.write(("m:"+button+":"+str(x)+":"+str(y)+"\n").encode('utf-8'))

def mouseMove(x, y, isBack):
    global mouseRatio
    x = int((x - 1024 / 2) * mouseRatio)
    y = int((y - 768 / 2) * mouseRatio)
    direction = 'f'
    if (isBack):
        direction = 'b'
    usb.write(("m:"+direction+":"+str(x)+":"+str(y)+"\n").encode('utf-8'))

def keyPress(key):
    usb.write(("k:"+key+"\n").encode('utf-8'))

def initBattle(x, y):
    global mouseRatio
    x = int((x - 1024 / 2) * mouseRatio)
    y = int((y - 768 / 2) * mouseRatio)
    # time.sleep(0.1)
    usb.write(("b:b:"+str(x)+":"+str(y)+"\n").encode('utf-8'))

def screenCap(saveImg):
    global screenTop, screenLeft
    with mss.mss() as sct:
        # The screen part to capture
        monitor = {'top': screenTop, 'left': screenLeft, 'width': 1024, 'height': 768}

        # Grab the data
        if saveImg:
            im = sct.grab(monitor)
            mss.tools.to_png(im.rgb, im.size, output="screenshot-"+str(int(time.time())) +".png")
            return np.array(im, dtype=np.uint8)
        return np.array(sct.grab(monitor), dtype=np.uint8)

def screenCapRect(top, left, width, height):
    global screenTop, screenLeft
    with mss.mss() as sct:
        # The screen part to capture
        monitor = {'top': screenTop+top, 'left': screenLeft+left, 'width': width, 'height': height}

        # Grab the data
        return np.array(sct.grab(monitor), dtype=np.uint8)

def imageORC(img):
    tessdata_dir_config = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata" -l eng --psm 6 --oem 0'
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

def checkAutoHunt():
    img = screenCapRect(324, 436, 167, 74)
    isAutoHuntReport = imageORC(img)
    if 'report has been' in isAutoHuntReport:
        print('------------In auto hunt report--------------')
        return True
    return False

def solveAutoHunt():
    time.sleep(1)
    mouseMoveClick('l', 625, 420)
    time.sleep(1)
    screenCap(True)
    mouseMove(820, 390, False)
    time.sleep(1)
    img = screenCapRect(280, 411, 202, 29)
    autoHuntType = imageORC(img)
    if 'Please type' in autoHuntType:
        img = screenCapRect(350, 418, 188, 58)
        engString = imageORC(img)
        engString = engString.replace(' ', '')
        for c in engString:
            keyPress(c)
            time.sleep(0.4)
        time.sleep(0.4)
        keyPress('*')
        mouseMove(820, 390, True)

    elif 'your answer' in autoHuntType:
        img = screenCapRect(350, 418, 188, 51)
        mathString = imageORC(img)
        mathString = mathString.replace('x', '*').replace('X', '*').replace('×', '*').replace('÷', '/').replace('_', '-')
        ans = eval(mathString)
        ANSBOXCOOR = [[451, 404, [440, 415]], [451, 425, [440, 435]], [501, 404, [490, 415]], [501, 425, [490, 435]], [551, 404, [540, 415]], [551, 425, [540, 435]]]
        for ansBox in ANSBOXCOOR:
            img = screenCapRect(ansBox[1], ansBox[0], 30, 19)
            ansOfAnsBox = imageORC(img)
            try:
                ansOfAnsBox = parseInt(ansOfAnsBox)
            except:
                ansOfAnsBox = 0
            if ansOfAnsBox == ans:
                mouseMove(820, 390, True)
                time.sleep(1)
                mouseMoveClick('l', ansBox[2][0], ansBox[2][1])
                break
    else:
        mouseMove(820, 390, True)
    time.sleep(1)


def checkBattleStartingPos(img):
    global leftPixel, rightPixel, topPixel, bottomPixel, leftMiddlePixel, rightMiddlePixel, battleColor
    if img[leftPixel[1]][leftPixel[0]][0] == battleColor and img[leftPixel[1]][leftPixel[0]][1] == 0 and img[leftPixel[1]][leftPixel[0]][2] == 0:
        print('left side')
        return 960, 405
    if img[rightPixel[1]][rightPixel[0]][0] == battleColor and img[rightPixel[1]][rightPixel[0]][1] == 0 and img[rightPixel[1]][rightPixel[0]][2] == 0:
        print('right side')
        return 40, 340
    if img[topPixel[1]][topPixel[0]][0] == battleColor and img[topPixel[1]][topPixel[0]][1] == 0 and img[topPixel[1]][topPixel[0]][2] == 0:
        print('top side')
        return 500, 600
    if img[bottomPixel[1]][bottomPixel[0]][0] == battleColor and img[bottomPixel[1]][bottomPixel[0]][1] == 0 and img[bottomPixel[1]][bottomPixel[0]][2] == 0:
        print('bottom side')
        return 500, 85
    if img[leftMiddlePixel[1]][leftMiddlePixel[0]][0] == battleColor and img[leftMiddlePixel[1]][leftMiddlePixel[0]][1] == 0 and img[leftMiddlePixel[1]][leftMiddlePixel[0]][2] == 0:
        print('left middle side')
        return 900, 130
    if img[rightMiddlePixel[1]][rightMiddlePixel[0]][0] == battleColor and img[rightMiddlePixel[1]][rightMiddlePixel[0]][1] == 0 and img[rightMiddlePixel[1]][rightMiddlePixel[0]][2] == 0:
        print('right middle side')
        return 80, 590
    return int(1024/2), int(768/2)

def checkStamina(img):
    x = 610 - int(1024 / 2)
    y = 390 - int(768 / 2)
    if img[669][190][0] != 66 or img[669][190][1] != 211 or img[669][190][2] != 165 or img[676][190][0] != 66 or img[676][190][1] != 211 or img[676][190][2] != 165:
        usb.write(("s:s:"+str(x)+":"+str(y)+"\n").encode('utf-8'))
        time.sleep(0.7)

def checkIsBattle(img):
    global isBattle, mapIconColor
    orc = screenCapRect(708, 837, 55, 17)
    checkedWord = imageORC(orc)
    if 'Battle' in checkedWord or 'Peace' in checkedWord:
        if isBattle is not False:
            print('Not in battle')
            isBattle = False
            checkStamina(img)

    else:
        if isBattle is not True:
            print('In battle')
            isBattle = True
            time.sleep(1.9)
            px, py = checkBattleStartingPos(screenCap(False))
            initBattle(px, py)
            print(datetime.datetime.now())

def selectMonster(box, score):
    global nextSelectMonsterTime
    # print(score)
    if (score > 0.67):
        minY = box[0] * 768
        minX = box[1] * 1024
        maxY = box[2] * 768
        maxX = box[3] * 1024
        # print(int(minX + (maxX - minX) / 2), int(minY + (maxY - minY) / 2))
        monsterX = int(minX + (maxX - minX) / 2)
        monsterY = int(minY + (maxY - minY) / 2)
        if (monsterX <= 975 and monsterY <= 750):
            mouseMoveClick('r', monsterX, monsterY)
            nextSelectMonsterTime = datetime.datetime.now() + datetime.timedelta(seconds=2)

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec) 
        func()  
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def main():
    global isBattle, nextSelectMonsterTime, pauseTime, pauseTimeEnd

    img = screenCap(False)
    # boxes, scores, classes, num = monsterDetector.get_classification(np.flip(img[:, :, :3], 2))
    # print(boxes[0][0], scores[0][0], classes[0][0], num)
    # print(img[3][1004])
    # print(img[36][1004])
    # print(img[5][988])
    # print(img[31][979])
    checkIsBattle(img)
    if isBattle == False and nextSelectMonsterTime < datetime.datetime.now():
    # if isBattle == False and nextSelectMonsterTime < datetime.datetime.now():
        # if pauseTimeEnd < datetime.datetime.now():
        #     pauseTime = datetime.datetime.now() + datetime.timedelta(seconds=45*60)
        #     pauseTimeEnd = datetime.datetime.now() + datetime.timedelta(seconds=60*60)
        # if pauseTime < datetime.datetime.now() and pauseTimeEnd > datetime.datetime.now():
        #     return 0
        if checkAutoHunt():
            solveAutoHunt()
        else:
            boxes, scores, classes, num = monsterDetector.get_classification(np.flip(img[:, :, :3], 2))
            selectMonster(boxes[0][0], scores[0][0])

initImg = screenCap(False)
monsterDetector.get_classification(np.flip(initImg[:, :, :3], 2))
mapIconColor = initImg[3][1004][1]

while True:
    # time.sleep(0.5)
    main()