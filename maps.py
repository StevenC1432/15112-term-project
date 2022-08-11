from helper import *

import math, pickle

class Map:
    def __init__(self):
        self.inDrawMode = True
        self.displayDots = True
        self.selectedIndex = []
        # get map points
        with open('map_points.pkl', 'rb') as file:
            mapPoints = pickle.load(file)
        # game map points
        self.trackLine    = mapPoints[0]
        self.interiorWall = self.scalePolygon(mapPoints[1], 10)
        self.exteriorWall = self.scalePolygon(mapPoints[2], 10)
        self.editingShape = []       
        # scale map points
        self.gameMap = self.scalePolygon(self.trackLine, 10)
        self.miniMap = self.scalePolygon(self.trackLine, 0.3)
        
        # SAVED MAP POINTS TO FILE #########################################
        # mapPoints = [self.trackLine, self.interiorWall, self.exteriorWall]
        # with open('map_points.pkl', 'wb') as file:
        #     pickle.dump(mapPoints, file)
        ####################################################################
    
    ##########
    # DRAW MAP
    ##########
    
    def draw(self, app, canvas):
        # draws map on selection screen
        if app.screen == "selection":
            displayTrack = self.scalePolygon(self.trackLine, 0.6)
            for index, (x, y) in enumerate(displayTrack):
                displayTrack[index] = (x+510, y+200)
            canvas.create_line(displayTrack, fill="grey", width=20)
            canvas.create_line(displayTrack, fill="black", width=1, dash=(2, 2))
        # draws scaled map for game
        elif app.screen == "game":
            # grass
            canvas.create_rectangle(0, 0, app.canvasWidth, app.canvasHeight, 
                                    fill="lightGreen")
            self.drawRaceTrack(canvas)
            self.drawRaceLine(canvas, self.gameMap)
    
    ##########################
    # RACE TRACK LANE/BARRIERS
    
    def drawRaceTrack(self, canvas):
        # track red/white indicators
        canvas.create_line(self.gameMap, fill="white", width=320)
        for i in range(1, len(self.gameMap)):
            p1, p2 = self.gameMap[i-1], self.gameMap[i]
            canvas.create_line(p1, p2, fill="red", dash=(50, 50), width=320)
        # trackbed
        canvas.create_line(self.gameMap, fill="grey", width=300)
        # track center line markings
        for i in range(1, len(self.gameMap)):
            p1, p2 = self.gameMap[i-1], self.gameMap[i]
            canvas.create_line(p1, p2, fill="black", dash=(10, 10), width=5)
        # barriers
        canvas.create_line(self.interiorWall, fill="grey", width=5)
        canvas.create_line(self.exteriorWall, fill="grey", width=5)

    #################
    # RACE START LINE

    def drawRaceLine(self, canvas, points):
        # align raceline to slope of track
        x, y = points[0][0]+400, points[0][1]+47
        x2, y2 = points[1][0]+400, points[1][1]+47
        slope = (x-x2) / (y-y2)
        # draw raceline
        self.alternatingSquares(canvas, x, y, slope, 0, 0)
        self.alternatingSquares(canvas, x, y, slope, 20, 1)
    
    # draws a pattern of alternating squares
    def alternatingSquares(self, canvas, x, y, slope, shift, oddStart):
        l, w = 150, 10
        raceline = [(x-w-shift, y-l), (x-w-shift, y+l), 
                    (x+w-shift, y+l), (x+w-shift, y-l)]
        for i in range(16):
            raceline[1] = (x-w-shift, y+l - 20*i)
            raceline[2] = (x+w-shift, y+l - 20*i)
            block = raceline[:]
            block = rotatePolygon(block, (x, y), slope)
            if i%2 == oddStart: canvas.create_polygon(block, fill="black")
            else: canvas.create_polygon(block, fill="white")

    # #######################
    # MAP EDITOR
    # Used to create game map
    #########################
    
    # commands used to add/remove/manipulate map points
    def userInput(self, inputType, action):
        if inputType == "keyPress":
            if action == "a":       self.addPoint()
            elif action == "r":     self.removePoint()
            elif action == "p":     print(self.editingShape)
            elif action == "m":     self.inDrawMode = not self.inDrawMode
            elif action == "x":     self.scaleMap(self.editingShape, 10)
            elif action == "d":     self.selectedIndex = []
            elif action == "c":     self.displayDots = not self.displayDots
            elif action == "Up":    self.movePoints(0, -1)
            elif action == "Down":  self.movePoints(0, 1)
            elif action == "Left":  self.movePoints(-1, 0)
            elif action == "Right": self.movePoints(1, 0)   
        elif inputType == "mousePress":
            # draws new point
            if self.inDrawMode: self.addPoint(action)
            # selects existing point
            else: self.selectPoint(action)

    # draws the shape being edited in the map editor
    def drawEditingShape(self, canvas, shape, r=2):
        if len(shape) > 1:
            canvas.create_line(shape, width=1, fill="red")
            if self.displayDots:
                for index, point in enumerate(shape):
                    (x, y) = point
                    color = "white" if index in self.selectedIndex else "black"
                    canvas.create_oval(x-r, y-r, x+r, y+r, fill=color)

    def addPoint(self, clickedPoint=None):
        # draw mode: creates new point at mouseclick
        if self.inDrawMode: self.editingShape.append(clickedPoint)
        # edit mode: creates new point near selected point
        elif len(self.selectedIndex) == 1: 
            (x, y)= self.editingShape[self.selectedIndex[0]]
            self.editingShape.insert(self.selectedIndex[0], (x+10, y))
            self.selectedIndex = []
    
    def removePoint(self):
        # draw mode: removes last drawn point
        if self.inDrawMode and self.editingShape: self.editingShape.pop()
        # edit mode: removes selected point
        elif len(self.selectedIndex) == 1: 
            self.editingShape.pop(self.selectedIndex[0])
            self.selectedIndex = []

    # edit mode: selects clicked point
    def selectPoint(self, clickedPoint):
        if not self.inDrawMode:
            for currentIndex, (x, y) in enumerate(self.editingShape):
                if distance((x, y), (clickedPoint)) < 5:
                    self.selectedIndex.append(currentIndex)

    # edit mode: shifts selected points
    def movePoints(self, dx, dy):
        for index, (x, y) in enumerate(self.editingShape):
            if index in self.selectedIndex:
                self.editingShape[index] = (x+dx, y+dy)
                    
    # scales polygon by given factor
    def scalePolygon(self, polygon, scale):
        scaled = polygon[:]
        for index, (x, y) in enumerate(polygon):
            x *= scale
            y *= scale
            scaled[index] = (x, y)
        return scaled