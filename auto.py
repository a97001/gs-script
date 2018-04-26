import numpy as np
import mss
import mss.tools
import threading

global screenTop, screenLeft, isBattle
screenTop = 227
screenLeft = 448
isBattle = False

def checkIsBattle(img):
    global isBattle
    if img[3][1004][1] == 198 and img[36][1004][1] == 198 and img[5][988][1] == 198 and img[31][979][1] == 198:
        if isBattle is not False:
            print('Not in battle')
            isBattle = False

    else:
        if isBattle is not True:
            print('In battle')
            isBattle = True

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec) 
        func()  
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def main():
    with mss.mss() as sct:
        # The screen part to capture
        monitor = {'top': screenTop, 'left': screenLeft, 'width': 1024, 'height': 768}

        # Grab the data
        img = np.array(sct.grab(monitor))

        print(img.shape)


        print(img[3][1004])
        print(img[36][1004])
        print(img[5][988])
        print(img[31][979])
        checkIsBattle(img)

t = set_interval(main, 1)