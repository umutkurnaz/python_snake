import tkinter as tk
import time
import threading
import random

from pynput import keyboard
from copy import copy

class Game_Window():
    def __init__(self, w, h, fps):
        self.w = w
        self.h = h
        self.border = ((w/25)-1, (h/25)-1)
        self.fps = fps
        self.currentlyOnFrame = []
        self.currentFrame = 0
        self.score = "0"
        self.main_window = tk.Tk()
        self.lbl = tk.Label(self.main_window, text="Oyun 3 Saniye İçersinde Başlıyor")
        self.canvas = tk.Canvas(self.main_window, bg="black", height=self.h, width=self.w)
        self.nextCanvas = tk.Canvas(self.main_window, bg="black", height=self.h, width=self.w)
        self.lbl.pack()
        self.canvas.pack()
    
    def start(self):
        self.main_window.update()
        self.startMainWindow()

    def setScore(self, score):
        self.score = score

    def increaseFrameCount(self):
        while 1:
            print(self.currentFrame)
            time.sleep(1)
            self.currentFrame += 1

    def startMainWindow(self):
        x = threading.Thread(target=self.increaseFrameCount)
        x.start()
        while 1:
            self.showWindow()
    
    def showWindow(self):
        self.paintNext()
        self.canvas.destroy()
        if self.currentFrame >= 3:
            self.lbl.destroy()
            self.lbl = tk.Label(self.main_window, text=self.score)
            self.lbl.pack()
        else:
            self.lbl.destroy()
            self.lbl = tk.Label(self.main_window, text="Oyun " + str(3-self.currentFrame) + " Saniye İçersinde Başlıyor")
            self.lbl.pack()
        self.canvas = self.nextCanvas
        self.nextCanvas = tk.Canvas(self.main_window, bg="black", height=self.h, width=self.w)
        self.canvas.pack()
        self.main_window.update()

    def paintNext(self):
        for item in self.currentlyOnFrame:
            rectangle = self.nextCanvas.create_rectangle(item["x0"], item["y0"], item["x1"], item["y1"], outline=item["color"], fill = item["color"]) 

    def addToCanvas(self, info):
        x = {
            "x0" : info[0],
            "y0" : info[1],
            "x1" : info[2],
            "y1" : info[3],
            "color" : info[4]
        }
        self.currentlyOnFrame.append(x)

    def deleteFromCanvas(self, info):
        x = {
            "x0" : info[0],
            "y0" : info[1],
            "x1" : info[2],
            "y1" : info[3],
            "color" : info[4]
        }
        if x in self.currentlyOnFrame:
            self.currentlyOnFrame.remove(x)

class Game_Object():
    def __init__(self, x, y, color, isActive):
        self.pos = (x, y)
        self.color = color
        self.isAlive = True
        self.isActive = isActive

    def changePos(self, x, y, border, body):
        if self.pos[0] + x > border[0] or self.pos[0] + x < 0:
            return 0

        if self.pos[1] + y > border[1] or self.pos[1] + y < 0:
            return 0

        info = [(25*(self.pos[0]+x)), (25*(self.pos[1]+y)), (25*((self.pos[0]+x)+1)), (25*((self.pos[1]+y)+1)),  self.color]

        for part in body:
            if info == part.getRender():
                if part != body[0]:
                    return 0
                else:
                    return 2

        newPos = (self.pos[0] + x, self.pos[1] + y)
        self.pos = newPos
        return 1

    def disableRender(self):
        self.isActive = False

    def enableRender(self):
        self.isActive = True

    def getRender(self):
        #x0, y0, x1, y1, color
        info = [(25*self.pos[0]), (25*self.pos[1]), (25*(self.pos[0]+1)), (25*(self.pos[1]+1)),  self.color]
        return info

class Snake():
    def __init__(self, x, y, color, isActive, game, inputs, speed):
        self.head = Game_Object(x, y, color, isActive)
        self.inputs = inputs
        self.body = []
        self.color = color
        self.isAlive = True
        self.game = game
        self.appleCount = 0
        self.listener = keyboard.Listener(on_press=self.input)
        self.listener.start() 
        self.direction = "right"
        self.speed = (1 / self.game.fps * speed)
        print(self.speed)
        thread = threading.Thread(target=self.start)
        thread.start()
        
    def start(self):
        self.getRender()
        while self.isAlive:
            self.move()
            time.sleep(self.speed)
        self.game.setScore("Öldünüz. Toplam Puanınız: " + str(self.appleCount))

    def input(self, key):
        try:
            k = key.char  # single-char keys
        except:
            k = key.name  # other keys
        
        if k in self.inputs and self.isAlive:
            canChange = True
            if k == "right":
                if len(self.body) != 0:
                    if self.head.pos[0] + 1 == self.body[0].pos[0]:
                        canChange = False
            elif k == "left":
                if len(self.body) != 0:
                    if self.head.pos[0] - 1 == self.body[0].pos[0]:
                        canChange = False
            elif k == "down":
                if len(self.body) != 0:
                    if self.head.pos[1] + 1 == self.body[0].pos[1]:
                        canChange = False
            elif k == "up":
                if len(self.body) != 0:
                    if self.head.pos[1] - 1 == self.body[0].pos[1]:
                        canChange = False

            if canChange:
                self.direction = k
        
        print('Key pressed: ' + k)

    def move(self):
        self.clearRender()
        hasEaten = self.isItApple()

        self.prevHead = copy(self.head)

        if self.direction == "right":
            result = self.head.changePos(1, 0, self.game.border, self.body)
        elif self.direction == "left":
            result = self.head.changePos(-1, 0, self.game.border, self.body)
        elif self.direction == "down":
            result = self.head.changePos(0, 1, self.game.border, self.body)
        elif self.direction == "up":
            result = self.head.changePos(0, -1, self.game.border, self.body)
        
        if result == 0:
            self.isAlive = False
        else:
            if len(self.body) != 0 and result == 1:
                self.body.insert(0, self.prevHead)
                self.body = self.body[:-1]

        self.getRender()

    def isItApple(self):
        info = self.head.getRender()
        if self.direction == "right":
            info[0] += 25
            info[2] += 25
        elif self.direction == "left":
            info[0] -= 25
            info[2] -= 25
        elif self.direction == "down":
            info[1] += 25
            info[3] += 25
        elif self.direction == "up":
            info[1] -= 25
            info[3] -= 25
        
        x = {
            "x0" : info[0],
            "y0" : info[1],
            "x1" : info[2],
            "y1" : info[3],
            "color" : "red"
        }

        if x in self.game.currentlyOnFrame:
            self.game.currentlyOnFrame.remove(x)
            self.appleCount += 1
            self.game.setScore(str(self.appleCount))
            newPos = (random.randint(0, self.game.border[0]), random.randint(0, self.game.border[1]))
            apple = Game_Object(newPos[0], newPos[1], "red", True)
            self.game.addToCanvas(apple.getRender())
            self.addToSnake(True)
            return True
        else:
            self.addToSnake(False)
            return False

    def addToSnake(self, hasEaten):
        if hasEaten:
            toAdd = copy(self.head)
            self.body.insert(0, toAdd)

    def clearRender(self):
        self.game.deleteFromCanvas(self.head.getRender())
        for part in self.body:
            self.game.deleteFromCanvas(part.getRender())

    def getRender(self):
        self.game.addToCanvas(self.head.getRender())
        for part in self.body:
            print(part.getRender())
            self.game.addToCanvas(part.getRender())

def createApple(game):
    apple = Game_Object(5 ,5, "red", True)
    time.sleep(3)
    game.addToCanvas(apple.getRender())
    createSnake(game)
    
def createSnake(game):
    print("Starting to draw in 5 seconds")
    i = ["left", "right", "down", "up"]
    snake = Snake(0, 0, "green", True, game, i, 3)
  
game = Game_Window(500, 500, 60)
thread = threading.Thread(target=createApple, args=(game, ))
thread.start()
game.start()