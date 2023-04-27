import cv2
import pytesseract
import PySimpleGUI as sg
import random
from picamera.array import PiRGBArray
from picamera import PiCamera
from unidecode import unidecode
from gpiozero import AngularServo
from time import sleep
from adafruit_servokit import ServoKit


import PySimpleGUI as sg

# ustawienia kamery
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera)
# ustawienia modułu PCA9685
kit = ServoKit(channels=16)
# tablica i ustawienia klawiatury
keys = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
chars = ''.join(keys)
lines = list(map(list, keys))
lines[0] += ["\u232B", "Esc"]
col = [[sg.Push()] + [sg.Button(key) for key in line] + [sg.Push()] for line in lines]
# ustawienia menu
layout = [[sg.Text("Praca inżynierska Hubert Orlicki")],
          [sg.Text('Zrób zdjęcie wyświetlanego tekstu i przetłumacz na Braille'),sg.Button("Zrób zdjęcie")],
          [sg.Text('Odgadnij literkę wyświetloną na wyświetlaczu'), sg.Button("Zgadnij literke")],
          [sg.InputText(key='-IN-'), sg.Button("Przetłumacz tekst na alfabet Braille")],
          [sg.Text('Uruchom klawiaturę dotykową'), sg.Button("Klawiatura")],
          [sg.Text('Przywróć ostatnio czytany tekst'), sg.Button("Przywróć")],
          [sg.pin(sg.Column(col, visible=False, expand_x=True, key='Column', metadata=False), expand_x=True)],
          [sg.Text('Zakończ działanie programu'), sg.Button("Zamknij")]]
window = sg.Window("Braille", layout)

# tablice tłumaczeń
brailleDotsLetters = ['⠁', '⠃', '⠉', '⠙', '⠑', '⠋', '⠛',
                      '⠓', '⠊', '⠚', '⠅', '⠇', '⠍','⠝', '⠕', '⠏', '⠟', '⠗',
                      '⠎', '⠞', '⠥', '⠧', '⠺', '⠭', '⠽', '⠵', ' ']
brailleDotsNumbers = ['⠼⠁', '⠼⠃', '⠼⠉', '⠼⠙', '⠼⠑', '⠼⠋',
                      '⠼⠛', '⠼⠓', '⠼⠊', '⠼⠚']
alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
            'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y', 'z', ' ']
numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

# tablice pozycji servo
servoPositionA = ['L:62', 'L:112', 'L:62|R:30', 'L:62|R:73', 'L:62|R:46', 'L:112|R:30', 'L:112|R:73',
                  'L:112|R:46', 'L:83|R:30', 'L:83|R:73', 'L:97', 'L:120', 'L:97|R:30', 'L:97|R:73', 'L:97|R:46',
                  'L:120|R:30','L:120|R:73', 'L:120|R:46',
                  'L:147|R:60', 'L:147|R:73', 'L:97|R:122', 'L:120|R:122', 'L:83|R:90', 'L:97|R:60', 'L:97|R:142',
                  'L:97|R:108', ' ']
servoPositionB = ['L:41', 'L:90', 'L:41|R:60', 'L:41|R:109', 'L:41|R:78', 'L:90|R:60', 'L:90|R:109',
                  'L:90|R:78', 'L:58|R:60', 'L:58|R:109', 'L:74', 'L:109', 'L:74|R:60', 'L:74|R:109', 'L:74|R:78',
                  'L:109|R:60','L:109|R:109', 'L:109|R:78',
                  'L:126|R:60', 'L:126|R:109', 'L:74|R:157', 'L:109|R:157', 'L:58|R:128', 'L:74|R:94', 'L:74|R:128',
                  'L:74|R:145', ' ']
servoPositionC = ['L:150', 'L:108', 'L:150|R:128', 'L:150|R:79', 'L:150|R:109', 'L:108|R:128', 'L:108|R:79',
                  'L:108|R:109', 'L:137|R:128', 'L:137|R:79', 'L:60', 'L:94', 'L:125|R:128', 'L:125|R:79', 'L:125|R:109',
                  'L:94|R:128','L:94|R:79', 'L:94|R:109',
                  'L:73|R:128', 'L:73|R:79', 'L:125|R:35', 'L:94|R:35', 'L:137|R:62', 'L:125|R:94', 'L:125|R:62',
                  'L:125|R:47', ' ']
servoPositionD = ['L:140', 'L:88', 'L:140|R:152', 'L:140|R:105', 'L:140|R:137', 'L:88|R:152', 'L:88|R:105',
                  'L:88|R:137', 'L:110|R:152', 'L:110|R:56', 'L:102', 'L:67', 'L:102|R:152', 'L:102|R:105',
                  'L:102|R:137', 'L:67|R:152','L:67|R:105', 'L:67|R:137',
                  'L:47|R:152', 'L:47|R:105', 'L:102|R:56', 'L:67|R:56', 'L:110|R:86', 'L:102|R:119', 'L:102|R:86', 'L:102|R:68', ' ']

# json wyboru silnika
servos = {
    'servoPositionA':{
        'L':'1',
        'R':'2',
    },
    'servoPositionB':{
        'L':'3',
        'R':'4',
    },
    'servoPositionC': {
        'L': '5',
        'R': '6',
    },
    'servoPositionD': {
        'L': '7',
        'R': '8',
    }
}



# główny kod odpowiadający za tłumaczenie
def translate_to_braille(translateToBraille):
    translatedText = ''

    if len(translateToBraille) > 0:
        for letter in translateToBraille.lower():
            if letter in alphabet:
                translatedText += brailleDotsLetters[alphabet.index(letter)]
            elif letter in numbers:
                translatedText += brailleDotsNumbers[numbers.index(letter)]
            else:
                print('Symbol: ' + translateToBraille + 'nie widnieje w bazie znaków')
        print('Twój text: ' + translateToBraille + ' ' + 'został przetłumaczony na: ' + translatedText)
        motors(translatedText)
    elif len(translateToBraille) == 0:
        print('Brak słów do tłumaczenia')

# funkcja sterujące prędkością ruchu silnika serwo
def rotate(number, position, angle, speed):
    howRotate = angle - position  # 90 - 0 = 90
    speed = speed / 10000
    print('Wartosc howRotate: ' + str(howRotate))
    if howRotate < 0:
        while position != angle:
            position += -1
            kit.servo[number].angle = position
            print('Aktualna pozycja: ' + str(position))
            sleep(speed)

    if howRotate > 0:
        while position != angle:
            position += 1
            kit.servo[number].angle = position
            print('Aktualna pozycja: ' + str(position))
            sleep(speed)

# funkcja sterowania silnikami
def motors(translatedText):
        servoCounter = 0
        for brailleDot in translatedText:
                # wybór silnika, kontrola pozycji serwo
                if brailleDot in brailleDotsLetters:
                    sleep(1)
                    if servoCounter < 4:
                        servoCounter = servoCounter + 1
                        print('counter: ' + str(servoCounter))
                    else:
                        servoCounter = 1
                        print('counter: ' + str(servoCounter))
                    if servoCounter == 1:
                        servoArray = servoPositionA
                        startL = 170
                        endL = 30
                        startR = 142
                        endR = 30
                        toJson = 'servoPositionA'
                    elif servoCounter == 2:
                        servoArray = servoPositionB
                        startL = 154
                        endL = 30
                        startR = 171
                        endR = 30
                        toJson = 'servoPositionB'
                    elif servoCounter == 3:
                        servoArray = servoPositionC
                        startL = 40
                        endL = 155
                        startR = 15
                        endR = 150
                        toJson = 'servoPositionC'
                    elif servoCounter == 4:
                        servoArray = servoPositionD
                        startL = 15
                        endL = 155
                        startR = 32
                        endR = 150
                        toJson = 'servoPositionD'
                    # rozbicie wartości z tablicy w celu przesłania odpowiedniej kombinacji do silnika w przypadku
                    # potrzeby wykorzystania dwóch silników dla jednego znaku
                    if '|' in str(servoArray[brailleDotsLetters.index(brailleDot)]):
                        servoSplit = servoArray[brailleDotsLetters.index(brailleDot)].split('|')
                        leftP = servoSplit[0].split(':')[1]
                        rightP = servoSplit[1].split(':')[1]
                        rotate(int(servos[toJson]['L']), startL, endL, 100)
                        rotate(int(servos[toJson]['L']), endL, int(leftP), 100)
                        sleep(1)
                        rotate(int(servos[toJson]['L']), int(leftP), startL, 100)

                        rotate(int(servos[toJson]['R']), startR, endR, 100)
                        rotate(int(servos[toJson]['R']), endR, int(rightP), 100)
                        sleep(1)
                        rotate(int(servos[toJson]['R']),int(rightP),startR,100)
                    # sterowanie pojedynczą częścią znaku (jednym silnikiem)
                    else:
                        if 'L' in str(servoArray[brailleDotsLetters.index(brailleDot)]):
                            leftP = servoArray[brailleDotsLetters.index(brailleDot)].split(':')[1]
                            print('Left: ' + servos[toJson]['L'])
                            position = int(servos[toJson]['L'])
                            rotate(int(servos[toJson]['L']), startL, endL, 100)
                            rotate(int(servos[toJson]['L']), endL, int(leftP), 100)
                            sleep(1)
                            rotate(int(servos[toJson]['L']), int(leftP), startL, 100)
                        else:
                            rightP = servoArray[brailleDotsLetters.index(brailleDot)].split(':')[1]
                            print('Right: ' + servos[toJson]['R'])
                            position = int(servos[toJson]['R'])
                            rotate(int(servos[toJson]['R']), startR, endR, 100)
                            rotate(int(servos[toJson]['R']), endR, int(rightP), 100)
                            sleep(1)
                            rotate(int(servos[toJson]['R']), int(rightP), startR, 100)
                else:
                    print('Brak pozycji dla tego symbolu: ' + brailleDot)


#
def translate_to_braille(translateToBraille):
    translatedText = ''
    with open('servoPosition.txt', 'w') as f:
        f.write(str(translateToBraille))
        f.write('\n')
    if len(translateToBraille) > 0:
        for letter in translateToBraille.lower():
            if letter in alphabet:
                translatedText += brailleDotsLetters[alphabet.index(letter)]
            elif letter in numbers:
                translatedText += brailleDotsNumbers[numbers.index(letter)]
            else:
                print('Symbol: ' + translateToBraille + 'nie widnieje w bazie znaków')
        print('Twój text: ' + translateToBraille + ' ' + 'został przetłumaczony na: ' + translatedText)
        motors(translatedText)
    elif len(translateToBraille) == 0:
        print('Brak słów do tłumaczenia')

# tłumaczenie alfabetu na znaki brajlowskie bez uruchomienia silników
def translate_without_motors(translateToBraille):
    translatedText = ''

    for letter in translateToBraille.lower():
        if letter in alphabet:
            translatedText += brailleDotsLetters[alphabet.index(letter)]
        elif letter in numbers:
            translatedText += brailleDotsNumbers[numbers.index(letter)]
        else:
            print('Symbol: ' + translateToBraille + 'nie widnieje w bazie znaków')
    print('Twój text: ' + translateToBraille + ' ' + 'został przetłumaczony na: ' + translatedText)

# funkcja przetwarzania obrazu i rozpoznawania znaków
def cameraMain():
     for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
         print('frame')
         image = frame.array
         cv2.imshow("Frame", image)
         key = cv2.waitKey(1) & 0xFF

         rawCapture.truncate(0)

         if key == ord("s"):
             translateToBraille = pytesseract.image_to_string(image)
             translateToBraille = translateToBraille.strip().replace(' ','')
             translateToBraille = unidecode(translateToBraille,'utf-8')
             translate_to_braille(translateToBraille)
             cv2.imshow("Frame", image)
             cv2.waitKey(0)
             break

     cv2.destroyAllWindows()

# sterowanie menu
while True:
    event, values = window.read()
    if event == "Zamknij" or event == sg.WIN_CLOSED:
        break
    elif event == "Zrób zdjęcie":
       cameraMain()
    elif event == "Zgadnij literke":
        letterToGuess = (random.choice(brailleDotsLetters))
        print(letterToGuess)
        motors(letterToGuess)
    elif event == "Przetłumacz tekst na alfabet Braille":
        text_input = values['-IN-']
        if len(text_input) > 1:
            text_input = unidecode(text_input, "utf-8")
            translate_without_motors(text_input)
        else:
            print('Wpisz tekst do przetłumaczenia')
    elif event == "Klawiatura":
        visible = window["Column"].metadata = not window["Column"].metadata
        window["Column"].update(visible=visible)
    elif event in chars:
        element = window.find_element_with_focus()
        if isinstance(element, sg.Input):
            if element.widget.select_present():
                element.widget.delete(sg.tk.SEL_FIRST, sg.tk.SEL_LAST)
            element.widget.insert(sg.tk.INSERT, event)
    elif event == "\u232B":
        element = window.find_element_with_focus()
        if element.widget.select_present():
            element.widget.delete(sg.tk.SEL_FIRST, sg.tk.SEL_LAST)
        else:
            insert = element.widget.index(sg.tk.INSERT)
            if insert > 0:
                element.widget.delete(insert - 1, insert)
    elif event == 'Esc':
        visible = window["Column"].metadata = not window["Column"].metadata
        window["Column"].update(visible=visible)
    elif event == 'Przywróć':
        with open('servoPosition.txt', 'r') as f:
            translate_to_braille(f.read())
    else:
        print('brak liter do tłumaczenia')

window.close()
