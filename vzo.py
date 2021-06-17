import pyautogui
import time
from PIL import ImageGrab
import requests
import pytesseract
import os
import sys

OVERBOUGHT = False
OVERSOLD = True

FIRST_PAIR_POSITION = (2352, 326)
COLOR_PIXEL_POSITION_X = [2301, 2303, 2305]
COLOR_PIXEL_POSITION_Y = 1293

COLOR_GREEN = (191, 223, 191)
COLOR_RED = (252, 208, 205)

GREEN_EMOJI = u'\U0001F7E2'
RED_EMOJI = u'\U0001F534'

TELEGRAM_CHAT_ID = 'x'
TELEGRAM_API_TOKEN = ''

# get Tesseract at https://github.com/UB-Mannheim/tesseract/wiki
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
SCREENSHOT_FILENAME = 'pair.png'
CHARTS_TXT = "ALL CHARTS AUTOMATION.txt"

def getVzoColor():
    color = (255, 255, 255)
    for position_x in COLOR_PIXEL_POSITION_X:        
        for i in range(0,10):
            try:
                currentColor = pyautogui.pixel(position_x, COLOR_PIXEL_POSITION_Y)
                if currentColor == COLOR_GREEN or currentColor == COLOR_RED:
                    color = currentColor
                break
            except OSError as e:
                continue

    return color

def chooseFirstPair():
    pyautogui.moveTo(FIRST_PAIR_POSITION[0], FIRST_PAIR_POSITION[1])
    pyautogui.doubleClick()
    time.sleep(2)

def chooseTimeframe():
    pyautogui.write(TIMEFRAME, interval=0.25)
    pyautogui.press('enter')
    time.sleep(2)

def isGreen(color):
    if color == COLOR_GREEN:
        return True

    return False

def isRed(color):
    if color == COLOR_RED:
        return True

    return False

def isRedOrGreen(color):
    if isGreen(color) or isRed(color):
        return True

    return False

def telegramMessage(text):
    url = f'https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage'
    data = {'chat_id': {TELEGRAM_CHAT_ID}, 'text': {text}}

    r = requests.post(url, data)

def telegramPhoto(caption):
    file = os.path.abspath(SCREENSHOT_FILENAME)

    files = {
        'photo': open(file, 'rb')
    }

    message = ('https://api.telegram.org/bot'+ TELEGRAM_API_TOKEN + '/sendPhoto?chat_id=' 
           + TELEGRAM_CHAT_ID + '&caption=' + caption)
    r = requests.post(message, files = files)

def prepare():
    pyautogui.leftClick()
    chooseTimeframe()

def getLineCount():
    file = open(CHARTS_TXT, "r")
    line_count = 0

    for line in file:
        if line != "\n":
            line_count += 1

    file.close()
    return line_count

def screenToText():
    im=ImageGrab.grab(bbox=(55,40,155,75))
    im.save(SCREENSHOT_FILENAME)

    return pytesseract.image_to_string(SCREENSHOT_FILENAME).strip()

def checkCharts():
    for i in range(0, PAIRS_AMOUNT):
        vzoColor = getVzoColor()

        if isRedOrGreen(vzoColor):
            text_pair = screenToText()
            state = GREEN_EMOJI if isGreen(vzoColor) else RED_EMOJI

            if (state == GREEN_EMOJI and OVERSOLD == False) or (state == RED_EMOJI and OVERBOUGHT == False):
                pyautogui.press('down')
                time.sleep(1)
                continue

            message = state + ' ' + text_pair + ' on ' + TIMEFRAME

            if text_pair:
                telegramMessage(message)
            else:
                telegramPhoto(message)

        pyautogui.press('down')
        time.sleep(1)


if len(sys.argv) < 2 or len(sys.argv) > 3:
    print('Call: python vzo.py <timeframe> <shutdown>')
    exit()

TIMEFRAME = sys.argv[1]
PAIRS_AMOUNT = getLineCount()

start_time = time.time()
prepare()
checkCharts()
print("--- %s seconds ---" % (time.time() - start_time))
# print(pyautogui.position())

if sys.argv[2] == 'shutdown':
    os.system("shutdown /s /t 1")