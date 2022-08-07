from cmu_112_graphics import *
from car import *
from maps import *
from helper import *

import math

def appStarted(app):
    # game settings
    app.canvasWidth, app.canvasHeight = 15000, 15000
    app.timerDelay = 1000//60
    app.screen = "selection"
    app.gameOver = True
    # create map
    app.map = Map()
    
    # TODO: load car image
    # track = app.loadImage("images/albert_park.jpeg")
    # track = app.scaleImage(track, 0.6)
    # app.track = ImageTk.PhotoImage(track)

def redrawAll(app, canvas):
    # set canvas scroll
    canvas.configure(xscrollincrement=1)
    canvas.configure(yscrollincrement=1)
    canvas.configure(scrollregion = (0, 0, app.canvasWidth, app.canvasHeight))
    # selection screen
    if app.screen == "selection":
        app.map.draw(app, canvas)
    # game screen
    elif app.screen == "game":
        if app.gameOver:
            return 
        app.map.draw(app, canvas)
        for car in app.cars:
            if car.racing:
                car.draw(app, canvas)
        # app.redbull.visualizeSelfDrive(app, canvas)

def setupCars(app): 
    # start positions
    x, y = app.map.gameMap[0][0]+400, app.map.gameMap[0][1]+47
    startPositions = [(x+100, y-50), (x+120, y+100),
                      (x+200, y-50), (x+220, y+100),
                      (x+300, y-50), (x+320, y+100),
                      (x+400, y-50), (x+420, y+100),
                      (x+500, y-50), (x+520, y+100)]
    # team information
    teams = {"Redbull":     ["green"], # TODO: add car images and logos
             "Ferrari":     ["red"],
             "Mercedes":    ["black"],
             "Alpine":      ["darkBlue"],
             "Mclaren":     ["orange"],
             "Alfaromeo":   ["darkGrey"],
             "Haas":        ["lightBlue"],
             "AlphaTauri":  ["darkRed"],
             "AstonMartin": ["turquoise"],
             "Williams":    ["blue"]
             }
    # create car objects
    app.cars = []
    player = "Williams"
    for index, name in enumerate(teams):
        color = teams[name][0]
        (x, y) = startPositions[index]
        if name == player:
            app.player = Player(app, name, x, y, color)
            app.cars.append(app.player)
        else:
            app.cars.append(Enemy(app, name, x, y, color))

def timerFired(app):
    if app.screen == "selection":
        pass
    else:
        for car in app.cars:
            if car.racing:
                if isinstance(car, Enemy):
                    car.checkpoints(app)
                    car.selfDrive(app)
                car.move(app)

def mousePressed(app, event):
    if app.screen == "selection":
        app.map.userInput("mousePress", (event.x, event.y))

def keyPressed(app, event):
    if app.screen == "selection":
        # starts game
        if event.key == "Space":
            app.screen = "game"
            app.gameOver = False
            setupCars(app)
        else:
            app.map.userInput("keyPress", event.key)
    elif app.screen == "game":
        if event.key == "w": app.player.pressedW()
        if event.key == "a": app.player.pressedA()
        if event.key == "d": app.player.pressedD()

def keyReleased(app, event):
    if app.screen == "game":
        if event.key == "w": app.player.releasedW()
        if event.key == "a": app.player.releasedA()
        if event.key == "d": app.player.releasedD()

runApp(width=1280, height=720)