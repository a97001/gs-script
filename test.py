import datetime
import numpy as np
import mss
import serial
import threading
import time

from MonsterDetector import MonsterDetector

screenTop = 227
screenLeft = 448


with mss.mss() as sct:
    # The screen part to capture
    monitor = {'top': screenTop, 'left': screenLeft, 'width': 1024, 'height': 768}

    # Grab the data
    img = np.array(sct.grab(monitor))
    print(img.shape)
    img = np.flip(img[:, :, :3], 2)
    print(img.shape)
    # boxes, scores, classes, num = monsterDetector.get_classification(img[:,:,:3])
    # print(boxes[0][0], scores[0][0], classes[0][0], num)
    # print(img[3][1004])
    # print(img[36][1004])
    # print(img[5][988])
    # print(img[31][979])
