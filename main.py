from cmu_112_graphics import *
from car import *
from maps import *
from button import *
from helper import *

import math

def appStarted(app):
    # game settings
    app.canvasWidth, app.canvasHeight = 15000, 15000
    app.timerDelay = 1000//60
    app.screen = "menu"
    app.gameOver = True
    app.paused = False
    # buttons
    app.menuButtons = []
    app.selectionButtons = []
    app.pausedButtons = []
    setUpButtons(app)
    # create map
    app.map = Map()
    loadImages(app)

def redrawAll(app, canvas):
    # set canvas scroll
    canvas.configure(xscrollincrement=1)
    canvas.configure(yscrollincrement=1)
    # menu screen
    if app.screen == "menu":
        drawMenu(app, canvas)
    # selection screen
    elif app.screen == "selection":
        canvas.configure(scrollregion = (0, 0, 1280, 640))
        drawSelection(app, canvas)
    # game screen
    elif app.screen == "game":
        canvas.configure(scrollregion = (0, 0, app.canvasWidth, app.canvasHeight))
        if app.gameOver:
            return 
        app.map.draw(app, canvas)
        for car in app.cars:
            if car.racing:
                car.draw(app, canvas)
        # app.redbull.visualizeSelfDrive(app, canvas)
        if app.paused:
            drawPausedMenu(app, canvas)

def startGame(app):
    app.screen = "game"
    app.gameOver = False
    app.paused = False
    setupCars(app)

def setupCars(app): 
    # start positions
    x, y = app.map.gameMap[0][0]+400, app.map.gameMap[0][1]+47
    startPositions = [(x+100, y-50), (x+175, y+60),
                      (x+250, y-40), (x+325, y+70),
                      (x+400, y-30), (x+475, y+80),
                      (x+550, y-20), (x+625, y+90),
                      (x+700, y-10), (x+775, y+100)]
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
    if app.screen == "game" and not app.paused:
        for car in app.cars:
            if car.racing:
                if isinstance(car, Enemy):
                    car.selfDrive(app)
                car.checkpoints(app)
                car.move(app)
        
        updateGameMenus(app)

def mousePressed(app, event):
    if app.screen == "menu":
        for button in app.menuButtons:
            if button.isClicked(event.x, event.y):
                buttonPressed(app, button)
    elif app.screen == "selection":
        for button in app.selectionButtons:
            if button.isClicked(event.x, event.y):
                buttonPressed(app, button)
        # map editing
        # app.map.userInput("mousePress", (event.x, event.y))
    elif app.screen == "game":
        for button in app.pausedButtons:
            if button.isClicked(event.x + app.player.xCamera-640, 
                                event.y + app.player.yCamera-360):
                buttonPressed(app, button)

def keyPressed(app, event):
    if app.screen == "selection":
        pass
        # map editing
        # app.map.userInput("keyPress", event.key)
    elif app.screen == "game":
        if event.key == "w": app.player.pressedW()
        if event.key == "a": app.player.pressedA()
        if event.key == "d": app.player.pressedD()
        if event.key == "Escape": app.paused = not app.paused

def keyReleased(app, event):
    if app.screen == "game":
        if event.key == "w": app.player.releasedW()
        if event.key == "a": app.player.releasedA()
        if event.key == "d": app.player.releasedD()
        
def setUpButtons(app):
    # menu screen
    startButton = Button("Start", app.width//2, app.height//2, 50, 25)
    quitButton = Button("Quit", app.width//2, app.height//2+70, 50, 25)
    app.menuButtons = [startButton, quitButton]
    # selection screen
    playButton = Button("Play", app.width//10, app.height//2, 50, 25)
    backButton = Button("Back", app.width//10, app.height//2+70, 50, 25)
    app.selectionButtons = [playButton, backButton]

def buttonPressed(app, button):
    if app.screen == "menu":
        if button.name == "Start": app.screen = "selection"
        elif button.name == "Quit": app.quit()
    elif app.screen == "selection":
        if button.name == "Play": startGame(app)
        elif button.name == "Back": app.screen = "menu"
    elif app.screen == "game" and app.paused:
        # reseting game also needs to reset canvas
        if button.name == "Resume": app.paused = False
        elif button.name == "Restart": startGame(app)
        elif button.name == "Exit": app.screen = "selection"

def drawMenu(app, canvas):
    for button in app.menuButtons:
        button.draw(canvas)
    # title
    canvas.create_image(app.width//2, app.height//2-100, image=app.logo)

def drawSelection(app, canvas):
    for button in app.selectionButtons:
        button.draw(canvas)
    app.map.draw(app, canvas)
    
def updateGameMenus(app):
    # game paused screen
    resumeButton = Button("Resume", app.player.xCamera, app.player.yCamera-70, 50, 25)
    restartButton = Button("Restart", app.player.xCamera, app.player.yCamera, 50, 25)
    exitButton = Button("Exit", app.player.xCamera, app.player.yCamera+70, 50, 25)
    app.pausedButtons = [resumeButton, restartButton, exitButton]
    
    # game over screen

def drawPausedMenu(app, canvas):
    # for button in app.pausedButtons:
    #     button.draw(canvas)
    drawGameOver(app, canvas)

def drawGameOver(app, canvas):
    cx, cy = app.player.xCamera, app.player.yCamera
    x, y = app.player.xCamera+150, app.player.yCamera
    w = 350
    l = 175
    # black background
    canvas.create_rectangle(cx-500, cy-300, cx+500, cy+300, fill="black")
    # winner background
    canvas.create_rectangle(cx-350-150, cy-300, cx-350+150, cy+300, fill="white")
    
    # leaderboard
    leader = app.player.rankings[len(app.player.rankings)-1][0]
    for index, (name, color, racing, laps, score, checkpointRank) in enumerate(app.player.rankings):
        standing = ((x-w, y-l), (x+w, y+l-35*index))
        if name == leader:
            fontColor = "black"
            rectColor = "white"
        else: 
            fontColor = "white"
            rectColor = "black"
        canvas.create_rectangle(standing, fill=rectColor, outline="black")
        canvas.create_text((x-310, y+l - 35*(index+1)+8), text=f"{10-index}", 
                            fill=fontColor, font="{Open Sans} 14", anchor="nw")
        canvas.create_text((x-280, y+l - 35*(index+1)+8), text=f"{name}", 
                            fill=fontColor, font="{Open Sans} 14", anchor="nw")
    
    # title text
    canvas.create_text(cx+20, cy-260, text="FORMULA 1 AUSTRALIAN GRAND PRIX",
                       fill="white", font="{Open Sans} 20 bold italic")
    canvas.create_text(cx-20, cy-220, text="CLASSIFICATION",
                       fill="grey", font="{Open Sans} 36 bold")
    canvas.create_text(cx+450, cy-190, text="TIME",
                       fill="white", font="{Open Sans} 16 bold")

def loadImages(app):
    logo = app.scaleImage(app.loadImage("images/f1logo.png"), 1)
    app.logo = ImageTk.PhotoImage(logo)

runApp(width=1280, height=720)