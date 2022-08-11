from cmu_112_graphics import *
from car import *
from maps import *
from button import *
from helper import *

import math
import pickle
from pygame import mixer

#######
# MODEL
#######

# initalizes game variables
def appStarted(app):
    mixer.init()
    # game settings
    app.canvasWidth, app.canvasHeight = 15000, 15000
    app.timerDelay = 1000//60
    app.screen = "menu"
    app.paused = False
    # setup game
    loadImages(app)
    setUpButtons(app)
    app.map = Map()
    app.time = 0
    app.inCountdown = True
    app.cx, app.cy = 0, 0
    # setup save file
    app.gameSaved = False
    with open('game_save.pkl', 'wb') as file:
        pickle.dump([], file)

# sets up new game
def startGame(app):
    app.screen = "game"
    app.paused = False
    # start position
    setupCars(app)
    app.inCountdown = True
    app.time = 0
    mixer.music.load("sounds/startSound.wav")
    mixer.music.set_volume(1)
    mixer.music.play()

#######################
# SET UP GAME VARIABLES

# sets up cars in starting positions
def setupCars(app): 
    # start positions
    x, y = app.map.gameMap[0][0]+400, app.map.gameMap[0][1]+47
    startPositions = [(x+100, y-50), (x+175, y+60),
                      (x+250, y-40), (x+325, y+70),
                      (x+400, y-30), (x+475, y+80),
                      (x+550, y-20), (x+625, y+90),
                      (x+700, y-10), (x+775, y+100)]

    # team information
    teams = {"Redbull":     ["#0600EF", app.redbullCar,  app.redbullLogo], 
             "Ferrari":     ["#DC0000", app.ferrariCar,  app.ferrariLogo],
             "Mercedes":    ["#00D2BE", app.mercedesCar, app.mercedesLogo],
             "Alpine":      ["#0090FF", app.alpineCar,   app.alpineLogo],
             "Mclaren":     ["#FF8700", app.mclarenCar,  app.mclarenLogo],
             "Alfaromeo":   ["#900000", app.romeoCar,    app.romeoLogo],
             "Haas":        ["#ED1A3B", app.haasCar,     app.haasLogo],
             "AlphaTauri":  ["#2B4562", app.tauriCar,    app.tauriLogo],
             "AstonMartin": ["#006F62", app.astonCar,    app.astonLogo],
             "Williams":    ["#005AFF", app.williamsCar, app.williamsLogo]
             }

    # create car objects
    app.cars = []
    player = "Williams"
    for index, name in enumerate(teams):
        color = teams[name][0]
        image = teams[name][1]
        logo  = teams[name][2]
        (x, y) = startPositions[index]
        if name == player:
            app.player = Player(app, name, x, y, color, image, logo)
            app.cars.append(app.player)
        else:
            app.cars.append(Enemy(app, name, x, y, color, image, logo))

# sets up game buttons
def setUpButtons(app):
    w, h = app.width//2, app.height//2
    # menu screen buttons
    startButton = Button("Start", w, h, 50, 25)
    quitButton  = Button("Quit", w, h+70, 50, 25)
    app.menuButtons = [startButton, quitButton]
    # selection screen buttons
    playButton = Button("Play", w-440, h-120, 50, 25)
    backButton = Button("Back", w-440, h-50, 50, 25)
    loadButton = Button("Load Game", w-440, h+150, 50, 25)
    app.selectionButtons = [playButton, backButton, loadButton]

# updates positions of game buttons as screen moves
def updateGameMenus(app):
    # game paused screen
    # TODO: add restart button
    resumeButton = Button("Resume", app.cx, app.cy-70, 50, 25)
    saveButton   = Button("Save", app.cx, app.cy, 50, 25)
    exitButton   = Button("Exit", app.cx, app.cy+70, 50, 25)
    app.pausedButtons = [resumeButton, saveButton, exitButton]
    # game over screen
    gameOverButton = Button("Exit", app.cx+420, app.cy+250, 50, 25, "white")
    app.gameOverButtons = [gameOverButton]

# loads game images
def loadImages(app):
    logo = app.loadImage("images/logos/f1logo.png")
    app.logo = ImageTk.PhotoImage(logo)
    
    carScale = 0.06
    app.redbullCar  = newImg(app, "images/cars/redbullCar.png",  carScale)
    app.ferrariCar  = newImg(app, "images/cars/ferrariCar.png",  carScale)
    app.mercedesCar = newImg(app, "images/cars/mercedesCar.png", carScale)
    app.alpineCar   = newImg(app, "images/cars/alpineCar.png",   carScale)
    app.mclarenCar  = newImg(app, "images/cars/mclarenCar.png",  carScale)
    app.romeoCar    = newImg(app, "images/cars/romeoCar.png",    carScale)
    app.haasCar     = newImg(app, "images/cars/haasCar.png",     carScale)
    app.tauriCar    = newImg(app, "images/cars/tauriCar.png",    carScale)
    app.astonCar    = newImg(app, "images/cars/astonCar.png",    carScale)
    app.williamsCar = newImg(app, "images/cars/williamsCar.png", carScale)
    
    app.redbullLogo  = newImg(app, "images/logos/redbullLogo.png")
    app.ferrariLogo  = newImg(app, "images/logos/ferrariLogo.png")
    app.mercedesLogo = newImg(app, "images/logos/mercedesLogo.png")
    app.alpineLogo   = newImg(app, "images/logos/alpineLogo.png")
    app.mclarenLogo  = newImg(app, "images/logos/mclarenLogo.png")
    app.romeoLogo    = newImg(app, "images/logos/romeoLogo.png")
    app.haasLogo     = newImg(app, "images/logos/haasLogo.png")
    app.tauriLogo    = newImg(app, "images/logos/tauriLogo.png")
    app.astonLogo    = newImg(app, "images/logos/astonLogo.png")
    app.williamsLogo = newImg(app, "images/logos/williamsLogo.png")

def newImg(app, path, scale=1):
    return app.scaleImage(app.loadImage(path), scale)

###############
# SAVE SESSIONS

def saveGame(app):
    # save all current car information    
    carInfo = {}
    for car in app.cars:
        if isinstance(car, Player): 
            carType = "player"
        else: 
            carType = f"enemy:{car.name}"
        carInfo[carType] = [car.name, car.x, car.y, car.color, car.image, 
                            car.logo, car.angle, car.score, car.laps, 
                            car.checkpointRank, car.racing]

    saveFile = [(app.cx, app.cy), (app.player.xShift, app.player.yShift), 
                carInfo]
    with open('game_save.pkl', 'wb') as file:
        pickle.dump(saveFile, file)

def loadGame(app):
    with open('game_save.pkl', 'rb') as file:
        saveFile = pickle.load(file)
    
    (app.player.xCamera, app.player.yCamera) = saveFile[0]
    app.player.gameLoaded(saveFile[1][0], saveFile[1][1])
    carInfo = saveFile[2]
    app.cars = []
    for car, info in carInfo.items():
        name  = info[0]
        x     = info[1]
        y     = info[2]
        color = info[3]
        image = info[4]
        logo  = info[5]
        angle = info[6]
        score = info[7]
        laps  = info[8]
        cRank = info[9]
        racing= info[10]
        if car == "player":
            app.player = Player(app, name, x, y, color, image, logo, angle,
                                score, laps, cRank, racing)
            app.cars.append(app.player)
        else:
            app.cars.append(Enemy(app, name, x, y, color, image, logo, angle,
                                    score, laps, cRank, racing))

############
# CONTROLLER
############

def timerFired(app):
    # check if game saved
    checkGameSave(app)
    if app.screen == "game" and not app.paused:
        # update variables:
        # - center of screen
        app.cx, app.cy = app.player.xCamera, app.player.yCamera
        # - rankings
        app.cars.sort(key=lambda x: (-x.score, x.checkpointRank), 
                      reverse=True)
        
        if app.inCountdown:
            # game start
            countdownLight(app)
        else:
            # gameplay
            carMovement(app)
            # dynamicDifficulty(app)
            playEngineSound(app)
        updateGameMenus(app)

##########################
# TIMER FIRED SUBFUNCTIONS

def checkGameSave(app):
    with open('game_save.pkl', 'rb') as file:
        saveFile = pickle.load(file)
    if saveFile == []:
        app.gameSaved = False
    else:
        app.gameSaved = True

def countdownLight(app):
    app.time += 10
    if app.time < 1200:
        return
    else:
        app.inCountdown = False
        app.time = 0
        mixer.music.stop()

def carMovement(app):
    for car in app.cars:
        if car.racing:
            if isinstance(car, Enemy):
                car.selfDrive(app)
            car.checkpoints(app)
            car.move(app)

def dynamicDifficulty(app):
    # slow down cars in front of player, speed up cars behind player
    if app.player in app.cars:
        playerIndex = app.cars.index(app.player)
        for carIndex in range(len(app.cars)):
            car = app.cars[carIndex]
            rankDiff = (playerIndex - carIndex)//2
            car.maxSpeed = 30 + rankDiff

def playEngineSound(app):
    if app.player.accelerating:
        if not app.inCountdown and not mixer.music.get_busy():
            mixer.music.load("sounds/carEngine.wav")
            mixer.music.set_volume(0.05)
            mixer.music.play()
    else:
        if mixer.music.get_volume() == 0.05:
            mixer.music.stop()

################
# BUTTON ACTIONS
                
def mousePressed(app, event):
    if app.screen == "menu":
        isButtonPressed(app, app.menuButtons, event.x, event.y)
    elif app.screen == "selection":
        isButtonPressed(app, app.selectionButtons, event.x, event.y)
        # MAP EDITING
        # app.map.userInput("mousePress", (event.x, event.y))
    elif app.screen == "game":
        # account for screen moving
        x = event.x + app.player.xCamera-640
        y = event.y + app.player.yCamera-360
        if app.paused:
            isButtonPressed(app, app.pausedButtons, x, y)
        elif not app.player.racing:
            isButtonPressed(app, app.gameOverButtons, x, y)

def isButtonPressed(app, buttonList, x, y):
    for button in buttonList:
        if button.pressed(x, y):
            action = button.name
            if app.screen == "menu":
                if action == "Start":  app.screen = "selection"
                if action == "Quit":   app.quit()
            if app.screen == "selection":
                if action == "Play": startGame(app)
                if action == "Load Game" and app.gameSaved: 
                    startGame(app)
                    loadGame(app)
                if action == "Back": app.screen = "menu"
            if app.screen == "game" and app.paused:
                # reseting game also needs to reset canvas
                if action == "Resume": app.paused = False
                if action == "Save":   saveGame(app); app.screen = "selection"
                if action == "Exit":   app.screen = "selection"
            elif app.screen == "game" and not app.player.racing:
                if button.name == "Exit": app.screen = "selection"

################

def keyPressed(app, event):
    if app.screen == "selection":
        pass
        # MAP EDITING
        # app.map.userInput("keyPress", event.key)
    elif app.screen == "game":
        if event.key == "w": app.player.pressedW()  
        if event.key == "a": app.player.pressedA()
        if event.key == "d": app.player.pressedD()
        if event.key == "Escape": 
            app.paused = not app.paused
            mixer.music.stop()
        if event.key == "l": app.player.racing = not app.player.racing # DEBUG

def keyReleased(app, event):
    if app.screen == "game":
        if event.key == "w": app.player.releasedW()
        if event.key == "a": app.player.releasedA()
        if event.key == "d": app.player.releasedD()
        
######
# VIEW
######

def redrawAll(app, canvas):
    # set canvas scroll
    canvas.configure(xscrollincrement=1)
    canvas.configure(yscrollincrement=1)
    # draw screens
    if app.screen == "menu":
        drawMenu(app, canvas)
    elif app.screen == "selection":
        drawSelection(app, canvas)
    elif app.screen == "game":
        drawGame(app, canvas)
        
#############
# MENU SCREEN

def drawMenu(app, canvas):
    for button in app.menuButtons:
        button.draw(canvas)
    # title
    canvas.create_image(app.width//2, app.height//2-100, image=app.logo)

##################
# SELECTION SCREEN

def drawSelection(app, canvas):
    canvas.configure(scrollregion = (0, 0, 1280, 640))
    # draw selection menu
    canvas.create_rectangle(90, 100, 310, 610)
    canvas.create_rectangle(310, 100, 1180, 610)
    canvas.create_text(200, 140, text="Main Menu", font="{Open Sans} 14")
    # draw load game option
    if app.gameSaved:
        savedText = "GAME SAVED"
        color = "PaleGreen3"
    else: 
        savedText = "NO GAME SAVED"
        color = "light coral"
    canvas.create_rectangle(100, 400, 300, 600, fill=color)
    canvas.create_text(200, 450, text=savedText, font="{Open Sans} 16 bold",
                       fill="white")
    
    for button in app.selectionButtons:
        button.draw(canvas)
    app.map.draw(app, canvas)
    # map description
    canvas.create_text(900, 150, text="AUSTRALIAN GRAND PRIX", 
                       font="{Open Sans} 30 bold")
    canvas.create_text(970, 190, text="ALBERT PARK, MELBOURNE", 
                       font="{Open Sans} 18 italic")

#############
# GAME SCREEN

def drawGame(app, canvas):
    canvas.configure(scrollregion = (0, 0, app.canvasWidth, app.canvasHeight))
    app.map.draw(app, canvas)
    # draw countdown light
    if app.inCountdown:
        drawCountdown(app, canvas)
    # draw cars
    for car in app.cars:
        if car.racing:
            car.draw(app, canvas)
    # game over screen
    if not app.player.racing:
        drawGameOver(app, canvas)
    # pause
    elif app.paused:
        drawPausedMenu(app, canvas)
        # drawGameOver(app, canvas) DEBUGGING
        
# draws animated start light at the beginning of the race
def drawCountdown(app, canvas):
    # draw bar
    canvas.create_rectangle(app.cx-150, app.cy-220, app.cx+150, app.cy-210, 
                            fill="grey", outline="black")
    
    for i in range(5):
        rx = app.cx-140 + i*70
        redLights = app.time // 200
        if i < redLights: 
            color = "red"
        else:
            color = "grey"
        # black box
        w, h = 30, 55
        canvas.create_rectangle(rx-w, app.cy-200-h, rx+w, app.cy-200+h, 
                                fill="black")
        # upper circles (decorative)
        r = 20
        canvas.create_oval(rx-r, app.cy-225-r, rx+r, app.cy-225+r, fill="grey")
        # lower circles (race signal)
        canvas.create_oval(rx-r, app.cy-175-r, rx+r, app.cy-175+r, fill=color)

# draws paused menu
def drawPausedMenu(app, canvas):
    for button in app.pausedButtons:
        button.draw(canvas)

###################
# GAME OVER DISPLAY

# draws game over screen after player finishes
def drawGameOver(app, canvas):
    mixer.music.stop()
    # black background
    canvas.create_rectangle(app.cx-500, app.cy-300, app.cx+500, app.cy+300, 
                            fill="black")
    # draw final standings
    drawResultTitle(app, canvas)
    drawTeamResults(app, canvas)
    drawWinner(app, canvas)
    # draw exit button
    for button in app.gameOverButtons:
        button.draw(canvas)
        
def drawResultTitle(app, canvas):
    canvas.create_text(app.cx+20, app.cy-260, 
                       text="FORMULA 1 AUSTRALIAN GRAND PRIX",
                       fill="white", font="{Open Sans} 20 bold italic")
    canvas.create_text(app.cx-20, app.cy-220, text="CLASSIFICATION",
                       fill="grey", font="{Open Sans} 36 bold")        
        
def drawTeamResults(app, canvas):
    i = 0
    for car in app.cars:
        # highlight first place in white # TODO: highlight player in green
        leader = app.cars[-1]
        if car.name == leader.name: 
            (fontColor, rectColor) = ("black", "white")
        else: 
            (fontColor, rectColor) = ("white", "black")

        w, l = 350, 175
        # ? make colors paler versions of team colors
        canvas.create_rectangle(app.cx+150 - w, app.cy-l,
                                app.cx+150 + w, app.cy+l - 35*i,
                                fill=rectColor, outline="black")
        # numerical ranks
        canvas.create_text((app.cx-190, app.cy+150 - 35*i), 
                           text=f"{10-i}", fill=fontColor, 
                           font="{Open Sans} 14", anchor="nw")
        # team names
        canvas.create_text((app.cx-150, app.cy+150 - 35*i), 
                           text=f"{car.name}", fill=fontColor, 
                           font="{Open Sans} 14", anchor="nw")
        i += 1
        # TODO: car finish times

def drawWinner(app, canvas):
    leader = app.cars[-1]
    # winner background
    canvas.create_rectangle(app.cx-500, app.cy-300, app.cx-200, app.cy+300, 
                            fill=leader.color)
    # winner text
    canvas.create_text(app.cx-350, app.cy+100, fill="white", 
                       text=leader.name, font="{Open Sans} 30")
    canvas.create_text(app.cx-350, app.cy+150, text="1st", fill="white", 
                       font="{Open Sans} 40 bold")
    # winner logo
    logo = ImageTk.PhotoImage(app.scaleImage(leader.logo, 0.6))
    canvas.create_image(app.cx-350, app.cy-50, image=logo)

###################

runApp(width=1280, height=720)